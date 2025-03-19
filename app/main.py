from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.routes.team_routes import team_router
from app.routes.user_routes import user_router
from app.utils import db


@asynccontextmanager
async def lifespan(_: FastAPI):
    pool = await db.connect()
    await db.initdb(pool)
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(team_router)
app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
