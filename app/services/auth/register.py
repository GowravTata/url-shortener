from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.config import USER_CREATION_SUCCESSFUL
from app.core.exceptions import UserAlreadyExists
from app.core.logging import AppLogger
from app.models.user import Users
from app.utils.password_checker import get_password_hash

logger = AppLogger().get_logger()


def register_user(email, password, db):
    """Register a new user with a hashed password; raises UserAlreadyExists if the email is taken."""
    try:
        email = email.lower().strip()
        logger.info(f"Started Registering User {email}")

        # Generate salt and hash the password
        hashed_password = get_password_hash(password=password)

        # Adding Entry into database
        new_entry = Users(
            email=email, password_hash=hashed_password, is_active=True
        )
        db.add(new_entry)
        db.commit()
        logger.info(f"User {email} registered successfully")
        return {"message": USER_CREATION_SUCCESSFUL}
    except IntegrityError as e:
        db.rollback()
        logger.exception(
            f"Failed Registering User {email}, Error: {str(e)}")
        raise UserAlreadyExists(
            message="User Already Exists",
            code="USER ALREADY EXISTS",
            context={"User Exists": email},
        )
    except Exception as e:
        logger.exception(
            f"Error occured while regsitering User: {email}, Error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
