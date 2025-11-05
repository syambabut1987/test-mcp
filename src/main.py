from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from repository import Repository
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.trace import (
    SpanKind,
    get_tracer_provider,
)
from opentelemetry.propagate import extract
from logging import getLogger, INFO

load_dotenv()

# Initialize OpenTelemetry with Azure Monitor
configure_azure_monitor(
    connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
)
tracer = trace.get_tracer(__name__, tracer_provider=get_tracer_provider())
logger = getLogger(__name__)
logger.setLevel(INFO)

# This schema is needed for POST request - /create endpoint
class Task(BaseModel):
    description: str
    user: str
    category: str

# Define the app
app = FastAPI(
    title="MyApp",
    description="Hello API developer!",
    version="0.1.0"
)

# Define CORS policy
origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize repository
repository = Repository(logger)

# API for health check of App
@app.get("/")
async def main(request: Request):
    with tracer.start_as_current_span(
        "main_request",
        context=extract(request.headers),
        kind=SpanKind.SERVER
    ):
        logger.info("Hello World endpoint was reached. . .")
        return {"message": "Hello World"}
    

# API to get all the data from ToDo list
@app.get("/all")
async def main(request: Request):
    with tracer.start_as_current_span("get_all_tasks",
                                      context=extract(request.headers),
                                      kind=SpanKind.SERVER):
        logger.info("Get all tasks endpoint was reached. . .")
        try:
            return await repository.get_all()
        except Exception as ex:
            logger.error(ex)
            return Response(content=str(ex), status_code=500)


# API to submit data to ToDo list
@app.post("/create")
async def submit(task: Task, request: Request):
    with tracer.start_as_current_span("create_task",
                                      context=extract(request.headers),
                                      kind=SpanKind.SERVER):
        logger.info("/create endpoint was reached. . .")
        try:
            await repository.add_task(task.description, task.user, task.category)
            return {"message": f"Data submitted successfully"}
        except Exception as ex:
            logger.error(ex)
            return Response(content=str(ex), status_code=500)


# API to mark a task as 'Completed'
@app.post("/done")
async def complete(task_id: int, request: Request):
    with tracer.start_as_current_span("mark_task_as_completed",
                                      context=extract(request.headers),
                                      kind=SpanKind.SERVER):
        logger.info("/done endpoint was reached. . .")
        try:
            await repository.update_task_status(task_id)
            return {"message": f"Task marked as completed successfully"}
        except Exception as ex:
            logger.error(ex)
            return Response(content=str(ex), status_code=500)