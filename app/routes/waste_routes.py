from fastapi import Body
from starlette import status
from starlette.responses import JSONResponse

from app.services import team_service, waste_service
from fastapi import APIRouter

waste_router = APIRouter()

@waste_router.post("/waste")
async def create_waste(
        type: str = Body(...),
        weight: float = Body(...),
        user_id: int = Body(...),
) -> JSONResponse:
    await waste_service.create_waste(type, weight, user_id)
    return JSONResponse(
        {"message": "Waste entry created successfully"}, status_code=status.HTTP_201_CREATED
    )
