from fastapi import HTTPException
from sqlalchemy import and_

from app.core.exceptions import InvalidUser
from app.core.logging import AppLogger
from app.core.security import create_access_token
from app.models.user import Users
from app.utils.password_checker import verify_password

logger = AppLogger().get_logger()


def user_login(email, password, db):
    """Authenticate a user by email and password, returning a JWT access token on success."""
    try:
        # Normalize email to keep lookup behavior case-insensitive.
        email = email.lower().strip()

        record = (
            db.query(Users)
            # Authenticate only active accounts.
            .filter(and_(Users.email == email, Users.is_active)).first()
        )

        if not record:
            logger.error(f"User not found: {email}")
            raise InvalidUser(
                message="User Not Found",
                code="INVALID_CREDENTIALS",
                context={"email": email},
            )

        is_password_correct = verify_password(password, record.password_hash)
        if not is_password_correct:
            raise InvalidUser(
                message="Invalid Password",
                code="INVALID_CREDENTIALS",
                context={"email": email},
            )
        data = {"user_id": record.id, "email": record.email}
        token = create_access_token(data)
        return {"access_token": token, "token_type": "bearer"}

    except InvalidUser:
        raise

    except Exception as e:
        logger.exception(f"Error logging user {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
