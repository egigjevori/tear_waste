import time
from unittest.mock import ANY

from app.utils.jwt import create_jwt, verify_jwt


async def test_jwt():
    jwt_token = create_jwt({"user": "admin", "exp": int(time.time()) + (3600 * 24)})  # Expires in 1 day

    result = verify_jwt(jwt_token)
    assert result["user"] == "admin"
    assert result["exp"] == ANY
