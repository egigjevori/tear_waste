from re import split

sample_user_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password",
    "role": "Employee",
    "team_id": 1,
}
async def test_login(patch_get_db_pool_user_service, patch_get_db_pool_team_service, client):
    # Send a POST request to the /user endpoint
    response = await client.post("/teams", data={"name": "New Team"})
    assert response.status_code == 201
    response = await client.post("/users", json=sample_user_data)
    assert response.status_code == 201
    response = await client.post("/login", json={
        "username": "testuser",
        "password": "password",
    })
    assert response.status_code == 200


    # Assert that the response body contains the expected message
    payload = response.json()["access_token"].split(".")[0]
    assert payload == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
