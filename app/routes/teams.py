from fastapi import Body
from starlette import status
from starlette.responses import JSONResponse

from app.main import app
from app.services import team_service


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/teams")
async def create_team(name: str = Body(...)) -> JSONResponse:
    await team_service.create_team(name)
    return JSONResponse(
        {"message": "Team created successfully"}, status_code=status.HTTP_201_CREATED
    )
