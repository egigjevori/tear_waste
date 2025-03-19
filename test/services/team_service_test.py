from app.services.team_service import create_team


async def test_create_team(get_team_repo_mock):
    # Arrange
    team_name = "Mock Team"

    # Act
    created_team = await create_team(name=team_name)

    # Assert
    assert created_team.id is not None
    assert created_team.name == team_name
