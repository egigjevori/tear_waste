from app.services.team_service import create_team
from app.services.user_service import create_user, delete_user, get_user

sample_user_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password",
    "role": "Employee",
    "team_id": 1,
}


async def test_create_user_success(get_user_repo_mock, get_team_repo_mock):

    # Sample user data for testing

    # Call the create_user function with the sample data
    team = await create_team(name="teamname")
    created_user = await create_user(**sample_user_data)

    # Assertions to verify the user was created correctly
    assert created_user.id is not None
    assert created_user.username == sample_user_data["username"]
    assert created_user.email == sample_user_data["email"]


async def test_delete(get_user_repo_mock, get_team_repo_mock):

    # Sample user data for testing
    team = await create_team(name="teamname")
    # Call the create_user function with the sample data
    created_user = await create_user(**sample_user_data)

    await delete_user(created_user.id)


async def test_get(get_user_repo_mock, get_team_repo_mock):

    # Sample user data for testing
    team = await create_team(name="teamname")
    # Call the create_user function with the sample data
    created_user = await create_user(**sample_user_data)
    created_user = await get_user(created_user.id)
    assert created_user.id is not None
    assert created_user.username == sample_user_data["username"]
    assert created_user.email == sample_user_data["email"]
