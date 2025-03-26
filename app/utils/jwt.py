import base64
import hashlib
import hmac
import json
import os
import time

SECRET_KEY = os.environ["SECRET_KEY"]

def base64_url_encode(data):
    """Encodes data to Base64 URL-safe format (without padding)."""
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

class JWTError(Exception):
    pass

def create_jwt(payload: dict) -> str:
    # Create the Header
    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header, separators=(",", ":")).encode()
    encoded_header = base64_url_encode(header_json)

    # Create the Payload
    payload_json = json.dumps(payload, separators=(",", ":")).encode()
    encoded_payload = base64_url_encode(payload_json)

    # Create the Signature
    message = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).digest()
    encoded_signature = base64_url_encode(signature)

    # Combine all parts
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def verify_jwt(token: str) -> dict:
    try:
        # Split token into parts
        encoded_header, encoded_payload, encoded_signature = token.split(".")

        # Decode header & payload
        decoded_payload = json.loads(base64.urlsafe_b64decode(encoded_payload + "==").decode())

        # Check expiration time
        if "exp" in decoded_payload and decoded_payload["exp"] < time.time():
            raise JWTError(f"Token expired")

        # Recalculate signature
        message = f"{encoded_header}.{encoded_payload}".encode()
        expected_signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).digest()
        expected_signature_encoded = base64_url_encode(expected_signature)

        # Validate signature
        if encoded_signature != expected_signature_encoded:
            raise JWTError("Token signature does not match")

        return decoded_payload
    except Exception as e:
        raise JWTError(f"Invalid token: {str(e)}")
