import pyodbc
import logging
import os
import datetime
from dotenv import load_dotenv

class Repository():
    def __init__(self, logger):
        print('Repository created')
        self.logger = logger

    # Initialize connection
    async def get_conn(self):
        try:
            load_dotenv()
            driver='{ODBC Driver 17 for SQL Server}'
            connection = pyodbc.connect(f'DRIVER={driver};SERVER=tcp:'+os.getenv("SQL_SERVER")+\
                                        '.database.windows.net;PORT=1433;DATABASE='+os.getenv("SQL_DB")+\
                                        ';UID='+os.getenv("SQL_USERNAME")+';PWD='+ os.getenv("SQL_PWD"))
            return connection
        except Exception as e:
            self.logger.error(e)
            raise e

    async def get_all(self) -> list|None:
        print('get_all called')
        try:
            # Get all items from the database
            connection = await self.get_conn()
            cursor = connection.cursor()
            cursor.execute("SELECT Id, Task, CreatedOn, CreatedBy, Category, IsCompleted, ModifiedOn FROM todolist")
            rows = cursor.fetchall()
            items = []
            for row in rows:
                items.append({
                    "id": row.Id,
                    "task": row.Task,
                    "createdOn": row.CreatedOn,
                    "createdBy": row.CreatedBy,
                    "category": row.Category,
                    "isCompleted": row.IsCompleted,
                    "modifiedOn": row.ModifiedOn
                })
            self.logger.info("All tasks retrieved successfully")
            return items
        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            cursor.close()
            connection.close()

    async def get_by_user(self, created_by_user: str) -> list|None:
        try:
        # Get all items from the database
            connection = await self.get_conn()
            cursor = connection.cursor()
            cursor.execute(f"SELECT Id, Task, CreatedOn, CreatedBy, Category, IsCompleted, ModifiedOn FROM todolist WHERE CreatedBy = {created_by_user}", created_by_user)
            rows = cursor.fetchall()
            items = []
            for row in rows:
                items.append({
                    "id": row.Id,
                    "task": row.Task,
                    "createdOn": row.CreatedOn,
                    "createdBy": row.CreatedBy,
                    "category": row.Category,
                    "isCompleted": row.IsCompleted,
                    "modifiedOn": row.ModifiedOn
                })
            self.logger.info(f"Tasks for user {created_by_user} retrieved successfully")
            return items
        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            cursor.close()
            connection.close()

    async def add_task(self, description: str, user: str, category: str) -> int:
        # Add a new item to the database
        try:
            INSERT_STATEMENT = "INSERT INTO todolist (Task, CreatedBy, CreatedOn, Category, IsCompleted) OUTPUT INSERTED.Id VALUES (?, ?, ?, ?, 0)"
            connection = await self.get_conn()
            cursor = connection.cursor()
            cursor.execute(INSERT_STATEMENT,
                            description,
                            user,
                            datetime.datetime.now(),
                            category)
            taskId = cursor.fetchval()
            connection.commit()
            self.logger.info(f"Task with {taskId} for user {user} added successfully")
            return taskId
        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            cursor.close()
            connection.close()

    async def update_task_status(self, task_id: int) -> None:
        # Update an item in the database
        try:
            UPDATE_STATEMENT = "UPDATE todolist SET IsCompleted = 1, ModifiedOn = ? WHERE Id = ?"
            connection = await self.get_conn()
            cursor = connection.cursor()
            cursor.execute(UPDATE_STATEMENT, datetime.datetime.now(), task_id)
            connection.commit()
            self.logger.info(f"Task with {task_id} updated successfully")
        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            cursor.close()
            connection.close()