async def test_get_all_teams(patch_get_db_pool_team_service, no_auth_client):

    # Send a POST request to the /teams endpoint
    response = await no_auth_client.post("/teams", json={"name": "New Team"})
    assert response.status_code == 201
    response = await no_auth_client.post("/teams", json={"name": "New Team 2"})
    assert response.status_code == 201
    response = await no_auth_client.get("/teams")

    assert response.json() == [
        {"id": 1, "name": "Admin"},
        {"id": 2, "name": "New Team"},
        {"id": 3, "name": "New Team 2"},
    ]


async def test_create_team(patch_get_db_pool_team_service, no_auth_client):
    # Define the payload for the POST request
    payload = {"name": "New Team"}

    # Send a POST request to the /teams endpoint
    response = await no_auth_client.post("/teams", json=payload)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response body contains the expected message
    assert response.json() == {"id": 2, "name": "New Team"}
