from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import IP, LOGIN, SIGNUP, USER
from app.core.db import get_db
from app.core.dependencies import rate_limit_dependency
from app.core.logging import AppLogger
from app.schemas.auth import UserRequest
from app.services.auth.login import user_login
from app.services.auth.register import register_user

auth_router = APIRouter(tags=["Authentication"], prefix="/v1/auth")
logger = AppLogger().get_logger()


@auth_router.post(
    "/register_user",
    summary="Register User in Database",
    description="API to get User Registered in the database",
    dependencies=[rate_limit_dependency(scope=SIGNUP, identifier_type=IP)],
)
async def user_registration(
    request: UserRequest, db: Session = Depends(get_db)
) -> dict:
    """Register a new user account with the provided email and password."""
    logger.info(f"Registration request received for {request.email}")
    return register_user(email=request.email, password=request.password, db=db)


@auth_router.post(
    "/login",
    summary="Login User to Application",
    description="API to get Login User to Application",
    dependencies=[rate_limit_dependency(scope=LOGIN, identifier_type=IP)],
)
async def login_user(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate a user via OAuth2 form payload and return a JWT access token."""
    logger.info(f"Login request received for {request.username}")
    return user_login(
        email=request.username,
        password=request.password,
        db=db,
    )


@auth_router.post(
    "/login-json",
    summary="Login User to Application using JSON",
    description="API to get Login User to Application",
    dependencies=[rate_limit_dependency(scope=LOGIN, identifier_type=IP)],
)
async def login_user_json(
    request: UserRequest,
    db: Session = Depends(get_db),
):
    """Authenticate a user via JSON body credentials and return a JWT access token."""
    logger.info(f"JSON login request received for {request.email}")
    return user_login(
        email=request.email,
        password=request.password,
        db=db,
    )
