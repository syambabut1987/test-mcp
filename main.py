import logging
import os
import pyodbc
import pandas as pd
# import json # Removed: The 'json' module is imported but not used in this script.
import azure.functions as func

# --- Configuration (These values should be set as Application Settings in your Function App) ---
# Environment variables are used for security and ease of deployment.
SERVER = os.environ.get('SQL_SERVER')
DATABASE = os.environ.get('SQL_DATABASE')
USERNAME = os.environ.get('SQL_USER')
PASSWORD = os.environ.get('SQL_PASSWORD')

# SQL query to run
SQL_QUERY = "SELECT OrderID, CustomerID, OrderDate, TotalAmount, Status FROM Orders"


def build_connection_string():
    """Constructs the ODBC connection string using environment variables."""
    if not all([SERVER, DATABASE, USERNAME, PASSWORD]):
        return None
        
    # Using the standard ODBC Driver 17 for SQL Server
    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={SERVER};'
        f'DATABASE={DATABASE};'
        f'UID={USERNAME};'
        f'PWD={PASSWORD};'
    )
    return conn_str

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    The main entry point for the HTTP-triggered Azure Function.
    Connects to Azure SQL and exports the Orders table data as CSV.
    """
    logging.info('Python HTTP trigger function processed a request to export Orders data.')

    conn_str = build_connection_string()
    
    if not conn_str:
        return func.HttpResponse(
            "Database connection settings (SQL_SERVER, SQL_DATABASE, SQL_USER, SQL_PASSWORD) are not configured.",
            status_code=500
        )

    try:
        # 1. Establish the connection
        with pyodbc.connect(conn_str) as conn:
            logging.info("Successfully connected to Azure SQL Database.")

            # 2. Execute the query and fetch data into a DataFrame
            # The read_sql_query function handles fetching all data efficiently
            df = pd.read_sql_query(SQL_QUERY, conn)
            logging.info(f"Successfully fetched {len(df)} rows from the Orders table.")

            if df.empty:
                 # If no data is found, return an informative response
                return func.HttpResponse(
                    "The query ran successfully, but no data was returned.",
                    status_code=204 # 204 No Content
                )

            # 3. Convert the DataFrame to CSV format
            # index=False ensures we don't include the pandas row index in the CSV
            csv_output = df.to_csv(index=False)
            
            # 4. Construct the HTTP Response
            return func.HttpResponse(
                csv_output,
                mimetype="text/csv",
                status_code=200,
                headers={
                    # This header tells the browser to download the response as a file
                    "Content-Disposition": "attachment; filename=orders_export.csv"
                }
            )

    except pyodbc.Error as ex:
        # Log the detailed database error
        sqlstate = ex.args[0]
        logging.error(f"Database error occurred: {sqlstate}")
        return func.HttpResponse(
             f"Database error: Could not connect or execute query. Details: {sqlstate}",
             status_code=500
        )
    except Exception as e:
        # Catch any other unexpected errors
        logging.error(f"An unexpected error occurred: {str(e)}")
        return func.HttpResponse(
            f"An unexpected error occurred: {str(e)}",
            status_code=500
        )

# Example package installation command for deployment:
# pip install pyodbc pandas
