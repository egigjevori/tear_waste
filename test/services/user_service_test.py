from app.services.user_service import create_user


sample_user_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password",
    "role": "Employee",
    "team_id": 1
}
async def test_create_user_success(get_user_repo_mock):

    # Sample user data for testing

    # Call the create_user function with the sample data
    created_user = await create_user(**sample_user_data)

    # Assertions to verify the user was created correctly
    assert created_user.id is not None
    assert created_user.username == sample_user_data["username"]
    assert created_user.email == sample_user_data["email"]
