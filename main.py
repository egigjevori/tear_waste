from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.utils import db




@asynccontextmanager
async def lifespan(_: FastAPI):
    await db.connect()
    await db.initdb()
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}
