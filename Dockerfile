# parent image
FROM python:3.10.9-slim-buster

EXPOSE 8000

WORKDIR /app

ADD /requirements.txt .
ADD /repository.py .
ADD /main.py .
# Uncomment the following line to use a local copy of the .env file
# ADD .env . 

RUN apt-get update -y && apt-get install -y curl gnupg g++ unixodbc-dev
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list 

RUN exit
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

COPY /odbc.ini / 
RUN odbcinst -i -s -f /odbc.ini -l
RUN cat /etc/odbc.ini 

RUN pip install --upgrade -r requirements.txt

# For running the container locally 
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app", "--worker-class", "uvicorn.workers.UvicornWorker"]
