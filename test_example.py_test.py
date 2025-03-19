import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import AsyncMock, patch
from main import app  # Assuming your FastAPI app is defined in main.py
from services.user_service import user_service  # Adjust the import based on your project structure


@pytest.mark.asyncio
async def test_get_users_by_team_id_success():
    # Mock data
    team_id = 1
    mock_users = [
        {"id": 1, "name": "John Doe", "team_id": team_id},
        {"id": 2, "name": "Jane Doe", "team_id": team_id},
    ]

    # Patch the user_service.get_users_by_team_id method
    with patch.object(user_service, "get_users_by_team_id", new=AsyncMock(return_value=mock_users)):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/users/by-team/{team_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_users


@pytest.mark.asyncio
async def test_get_users_by_team_id_not_found():
    # Mock data
    team_id = 999

    # Patch the user_service.get_users_by_team_id method to raise a ValueError
    with patch.object(user_service, "get_users_by_team_id", new=AsyncMock(side_effect=ValueError("Team not found"))):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/users/by-team/{team_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Team not found"}
