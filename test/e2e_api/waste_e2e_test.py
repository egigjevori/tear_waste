


sample_waste_data = {
    "type": "trash",
    "weight": 3.4,
    "user_id": 1
}

async def test_create_waste(patch_get_db_pool_waste_service, client):
    # Send a POST request to the /user endpoint
    response = await client.post("/waste", json=sample_waste_data)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response body contains the expected message
    assert response.json() == {"message": "Waste entry created successfully"}
