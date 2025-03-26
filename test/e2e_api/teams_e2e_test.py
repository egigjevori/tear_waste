async def test_create_team(patch_get_db_pool_team_service, no_auth_client):
    # Define the payload for the POST request
    payload = {"name": "New Team"}

    # Send a POST request to the /teams endpoint
    response = await no_auth_client.post("/teams", data=payload)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response body contains the expected message
    assert response.json() == {"message": "Team created successfully"}
