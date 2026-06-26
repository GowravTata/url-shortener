from datetime import datetime, timedelta

from jose import jwt

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


def create_access_token(data: dict):
    """Create a signed JWT access token with an expiry from the provided payload data."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM)
    return encoded_jwt
