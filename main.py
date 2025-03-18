from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.utils import db




@asynccontextmanager
async def lifespan(_: FastAPI):
    pool = await db.connect()
    await db.initdb(pool)
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}
