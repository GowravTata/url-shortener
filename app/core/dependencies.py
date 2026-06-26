from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import ALGORITHM, SECRET_KEY, USER
from app.core.logging import AppLogger
from app.utils.ip_limiter import check_rate_limit

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")
logger = AppLogger().get_logger()


def get_current_token(token: str = Depends(oauth2_scheme)):
    """Decode and validate the JWT bearer token, returning its payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            logger.warning("JWT payload missing user_id")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
            )
        return payload
    except JWTError:
        logger.warning("JWT validation failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )


def get_current_user_id(payload: dict = Depends(get_current_token)) -> int:
    """Return authenticated user_id extracted from JWT payload."""
    user_id = payload.get("user_id")
    try:
        return int(user_id)
    except (TypeError, ValueError):
        logger.warning("Unable to parse user_id from token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )


def rate_limit_dependency(scope: str, identifier_type: str):
    def dependency(
        request: Request,
        user_id: int | None = (
            Depends(get_current_user_id) if identifier_type == USER else None
        ),
    ):
        if identifier_type == USER:
            # Authenticated routes are throttled per user identity.
            identifier = f"user:{user_id}"
        else:
            # Public routes are throttled by caller IP (proxy-aware when header is set).
            forwarded = request.headers.get("X-Forwarded-For")
            identifier = (
                forwarded.split(",")[0].strip()
                if forwarded
                else request.client.host
            )
            identifier = f"ip:{identifier}"
        logger.info(
            f"Applying rate limit scope={scope} " f"identifier={identifier}"
        )
        check_rate_limit(scope=scope, identifier=identifier)

    return Depends(dependency)
