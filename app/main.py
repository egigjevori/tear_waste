from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request

from app.routes.authentication_routes import authentication_router
from app.routes.team_routes import team_router
from app.routes.user_routes import user_router
from app.routes.waste_routes import waste_router
from app.services import authentication_service
from app.services.authentication_service import AuthenticationError
from app.services.authorization_service import AuthorizationError
from app.utils import db


@asynccontextmanager
async def lifespan(_: FastAPI):
    pool = await db.connect()
    await db.initdb(pool)
    yield
    await db.disconnect()


# TODO global error handling
app = FastAPI(lifespan=lifespan)

app.include_router(authentication_router)
app.include_router(team_router)
app.include_router(user_router)
app.include_router(waste_router)


@app.middleware("authentication")
async def authentication(request: Request, call_next):
    if request.url.path == "/login":
        return await call_next(request)

    token = request.headers.get("Authorization")
    user = await authentication_service.verify_authentication(token)
    request.state.user = user

    response = await call_next(request)
    return response


@app.exception_handler(ValueError)
async def value_error_exception_handler(_: Request, exc: ValueError):
    raise HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(AuthenticationError)
async def authentication_error_exception_handler(_: Request, exc: AuthenticationError):
    raise HTTPException(status_code=401, detail=str(exc))


@app.exception_handler(AuthorizationError)
async def authorization_error_exception_handler(_: Request, exc: AuthorizationError):
    raise HTTPException(status_code=401, detail=str(exc))


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

# TODO rate limit
# TODO add cache
