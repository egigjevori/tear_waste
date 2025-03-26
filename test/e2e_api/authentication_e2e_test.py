from re import split

from app.models.users import UserRole
from app.services import authentication_service

sample_user_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password",
    "role": "Employee",
    "team_id": 1,
}


async def test_login(patch_get_db_pool_user_service, patch_get_db_pool_team_service, no_auth_client):
    # Send a POST request to the /user endpoint
    response = await no_auth_client.post("/teams", data={"name": "New Team"})
    assert response.status_code == 201
    response = await no_auth_client.post("/users", json=sample_user_data)
    assert response.status_code == 201
    response = await no_auth_client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "password",
        },
    )
    assert response.status_code == 200

    # Assert that the response body contains the expected message
    payload = response.json()["access_token"].split(".")[0]
    assert payload == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"


async def test_authentication(patch_get_db_pool_user_service, patch_get_db_pool_team_service, no_auth_client):
    # Send a POST request to the /user endpoint
    response = await no_auth_client.post("/teams", data={"name": "New Team"})
    assert response.status_code == 201
    response = await no_auth_client.post("/users", json=sample_user_data)
    assert response.status_code == 201
    response = await no_auth_client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "password",
        },
    )
    assert response.status_code == 200

    user = await authentication_service.verify_authentication(f"Bearer {response.json()['access_token']}")
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    assert user.role == UserRole.EMPLOYEE
    assert user.team_id == 1

    # Assert that the response body contains the expected message
    payload = response.json()["access_token"].split(".")[0]
    assert payload == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
