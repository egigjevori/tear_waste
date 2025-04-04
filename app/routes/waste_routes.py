import logging

from fastapi import APIRouter, Body, Request
from starlette import status
from starlette.responses import JSONResponse

from app.services import authorization_service, waste_service
from app.utils.permissions import Permission

logger = logging.getLogger(__name__)
waste_router = APIRouter()


def construct_waste_entries_data(waste_entries):
    return [entry.to_dict() for entry in waste_entries]


@waste_router.post("/waste")
@authorization_service.require_permission(Permission.CREATE_WASTE)
async def create_waste(
    request: Request,
    type: str = Body(...),
    weight: float = Body(...),
    user_id: int = Body(...),
) -> JSONResponse:
    logger.info(f"Attempting to create waste entry with type: {type}, weight: {weight}, user_id: {user_id}")

    waste = await waste_service.create_waste(type, weight, user_id)

    logger.info(f"Waste entry created successfully for user_id: {user_id}")
    return JSONResponse(waste.to_dict(), status_code=status.HTTP_201_CREATED)


@waste_router.get("/waste/user/{user_id}")
@authorization_service.require_permission(Permission.GET_WASTE_BY_USER_ID)
async def get_waste_by_user_id(request: Request, user_id: int) -> JSONResponse:
    logger.info(f"Fetching waste entries for user_id: {user_id}")

    waste_entries = await waste_service.get_waste_by_user_id(user_id)

    logger.info(f"Found {len(waste_entries)} waste entries for user_id: {user_id}")

    waste_entries_data = construct_waste_entries_data(waste_entries)

    return JSONResponse(content=waste_entries_data, status_code=status.HTTP_200_OK)
