import logging

sample_user_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password",
    "role": "Employee",
    "team_id": 1
}

async def test_create_user(patch_get_db_pool_user_service, client):
    # Send a POST request to the /user endpoint
    response = await client.post("/users", json=sample_user_data)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response body contains the expected message
    assert response.json() == {"message": "User created successfully"}
