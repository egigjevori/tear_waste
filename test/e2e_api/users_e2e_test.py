import logging

sample_user_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password",
    "role": "Employee",
    "team_id": 1,
}
cnt = 0


def create_test_user_data() -> dict:
    """Utility function to create a User object with predefined data for testing."""
    global cnt
    user = {
        "username": f"testuser{cnt}",
        "email": f"{cnt}testuser@example.com",
        "password": "password",
        "role": "Employee",
        "team_id": 1,
    }
    cnt += 1
    return user


async def test_create_user(patch_get_db_pool_user_service, patch_get_db_pool_team_service, no_auth_client):
    # Send a POST request to the /user endpoint
    response = await no_auth_client.post("/teams", data={"name": "New Team"})
    assert response.status_code == 201
    response = await no_auth_client.post("/users", json=sample_user_data)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response body contains the expected message
    assert response.json() == {"message": "User created successfully"}


async def test_get_users_by_team_id(patch_get_db_pool_user_service, patch_get_db_pool_team_service, no_auth_client):
    # Send a POST request to the /user endpoint
    response = await no_auth_client.post("/teams", data={"name": "New Team"})
    assert response.status_code == 201
    response = await no_auth_client.post("/users", json=create_test_user_data())
    assert response.status_code == 201
    response = await no_auth_client.post("/users", json=create_test_user_data())
    assert response.status_code == 201
    response = await no_auth_client.get("/users/by-team/1")

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 200

    # Assert that the response body contains the expected message
    assert response.json() == [
        {"email": "0testuser@example.com", "role": "Employee", "team_id": 1, "username": "testuser0"},
        {"email": "1testuser@example.com", "role": "Employee", "team_id": 1, "username": "testuser1"},
    ]
