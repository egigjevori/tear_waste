from app.services.user_service import create_user
from app.services.waste_service import create_waste

sample_waste_data = {
    "type": "trash",
    "weight": 3.4,
    "user_id": 1
}
async def test_create_waste_success(get_waste_repo_mock):

    # Sample user data for testing

    # Call the create_user function with the sample data
    created_waste = await create_waste(**sample_waste_data)

    # Assertions to verify the user was created correctly
    assert created_waste.id is not None
    assert created_waste.type == sample_waste_data["type"]
    assert created_waste.weight == sample_waste_data["weight"]
