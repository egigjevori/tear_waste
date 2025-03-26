import logging
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.routes.authentication_routes import authentication_router
from app.routes.team_routes import team_router
from app.routes.user_routes import user_router
from app.routes.waste_routes import waste_router
from app.services import authentication_service
from app.services.authentication_service import AuthenticationError
from app.services.authorization_service import AuthorizationError
from app.utils import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add console handler for logging
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
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        # Add the request ID to the log context
        logger = logging.getLogger("uvicorn")
        logger.info(f"Request ID: {request_id} - {request.method} {request.url}")

        # Store request ID in state for later use (e.g., in route handlers)
        request.state.request_id = request_id

        # Proceed with the request and capture response
        response = await call_next(request)

        # Log response with the same request ID
        logger.info(f"Request ID: {request_id} - Response Status: {response.status_code}")
        return response

# Add middleware to the FastAPI app
app.add_middleware(LogRequestMiddleware)
app.include_router(authentication_router)
app.include_router(team_router)
app.include_router(user_router)
app.include_router(waste_router)

@app.middleware("authentication")
async def authentication(request: Request, call_next):
    logger.info(f"Authenticating request for path: {request.url.path}")
    if request.url.path == "/login":
        return await call_next(request)

    token = request.headers.get("Authorization")
    try:
        user = await authentication_service.verify_authentication(token)
        request.state.user = user
        logger.info(f"User authenticated: {user}")
    except AuthenticationError as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

    response = await call_next(request)
    return response

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

@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Hello World"}

if __name__ == "__main__":
    logger.info("Starting the application...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    logger.info("Application shutdown.")

# TODO rate limit
# TODO add cache