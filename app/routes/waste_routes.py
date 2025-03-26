from typing import List

from fastapi import Body, Request
from starlette import status
from starlette.responses import JSONResponse

from app.models.waste import WasteEntry
from app.services import team_service, waste_service
from fastapi import APIRouter

waste_router = APIRouter()


@waste_router.post("/waste")
async def create_waste(
    request: Request,
    type: str = Body(...),
    weight: float = Body(...),
    user_id: int = Body(...),
) -> JSONResponse:
    await waste_service.create_waste(type, weight, user_id)
    return JSONResponse({"message": "Waste entry created successfully"}, status_code=status.HTTP_201_CREATED)


@waste_router.get("/waste/user/{user_id}")
async def get_waste_by_user_id(request: Request, user_id: int) -> JSONResponse:
    waste_entries = await waste_service.get_waste_by_user_id(user_id)

    # Manually construct the JSON response
    waste_entries_data = [
        {
            "id": entry.id,
            "type": entry.type,
            "weight": entry.weight,
            "timestamp": entry.timestamp.isoformat(),
            "user_id": entry.user_id,
        }
        for entry in waste_entries
    ]

    return JSONResponse(content=waste_entries_data, status_code=status.HTTP_200_OK)

@waste_router.get("/waste/team/{team_id}")
async def get_waste_by_team_id(request: Request, team_id: int) -> JSONResponse:
    #TODO if logged in user is manager, check for access to team
    waste_entries = await waste_service.get_waste_by_team_id(team_id)

    waste_entries_data = [
        {
            "id": entry.id,
            "type": entry.type,
            "weight": entry.weight,
            "timestamp": entry.timestamp.isoformat(),
            "user_id": entry.user_id,
        }
        for entry in waste_entries
    ]

    return JSONResponse(content=waste_entries_data, status_code=status.HTTP_200_OK)
