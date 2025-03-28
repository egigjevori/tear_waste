import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.routes.authentication_routes import authentication_router
from app.routes.team_routes import team_router
from app.routes.user_routes import user_router
from app.routes.waste_routes import waste_router
from app.services.authentication_service import AuthenticationError
from app.services.authorization_service import AuthorizationError
from app.utils import db
from app.utils.db import DatabaseError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


@asynccontextmanager
async def lifespan(_: FastAPI):
    pool = await db.connect()
    await db.initdb(pool)
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())

        logger = logging.getLogger("uvicorn")
        logger.info(f"Request ID: {request_id} - {request.method} {request.url}")

        request.state.request_id = request_id

        response = await call_next(request)

        logger.info(f"Request ID: {request_id} - Response Status: {response.status_code}")
        return response


# Add middleware to the FastAPI app
app.add_middleware(LogRequestMiddleware)
app.include_router(authentication_router)
app.include_router(team_router)
app.include_router(user_router)
app.include_router(waste_router)


@app.exception_handler(ValueError)
async def value_error_exception_handler(_: Request, exc: ValueError):
    logger.error(f"ValueError occurred: {str(exc)}")
    raise HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(AuthenticationError)
async def authentication_error_exception_handler(_: Request, exc: AuthenticationError):
    logger.error(f"AuthenticationError occurred: {str(exc)}")
    raise HTTPException(status_code=401, detail=str(exc))


@app.exception_handler(AuthorizationError)
async def authorization_error_exception_handler(_: Request, exc: AuthorizationError):
    logger.error(f"AuthorizationError occurred: {str(exc)}")
    raise HTTPException(status_code=401, detail=str(exc))


@app.exception_handler(DatabaseError)
async def database_error_exception_handler(_: Request, exc: DatabaseError):
    logger.error(f"DatabaseError occurred: {str(exc)}")
    raise HTTPException(status_code=400, detail=str(exc))


@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Hello World"}
