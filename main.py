import os
import json
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api.v1.api import router

from helpers.logger_config import setup_logger

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

logger = setup_logger()
logger.info("Application starting...")

APP_NAME = os.getenv("APP_NAME", "Multi Vendor Inventory Management System")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
PORT = int(os.getenv("PORT", 8000))
IS_PROD = os.getenv("IS_PROD", "false").lower() == "true"

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/backend/api/v1/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = exc.errors()
    logger.error(f"Validation Error: {error_details}")
    try:
        body = await request.body()
        if body:
            logger.error(f"Request Body: {body.decode()}")
    except Exception:
        pass

    return JSONResponse(
        status_code=422,
        content={"detail": error_details},
    )


@app.get("/")
async def root():
    return {"message": f"Welcome to {APP_NAME} v{APP_VERSION}"}


app.include_router(router, prefix="/backend/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=PORT,
        reload=not IS_PROD,
    )
