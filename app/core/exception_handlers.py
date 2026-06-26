from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.logging import AppLogger


async def url_not_found_handler(request: Request, exc: Exception):
    """Handle RecordNotFoundError and return a 404 JSON response."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.message,
            "code": exc.code,
            "context": exc.context,
        },
    )


async def url_expired_handler(request: Request, exc: Exception):
    """Handle URLExpiredError and return a 410 Gone JSON response."""
    return JSONResponse(
        status_code=status.HTTP_410_GONE,
        content={
            "detail": exc.message,
            "code": exc.code,
            "context": exc.context,
        },
    )


async def url_deleted_handler(request: Request, exc: Exception):
    """Handle URLDeletedError and return a 404 JSON response."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": exc.message,
            "code": exc.code,
            "context": exc.context,
        },
    )


async def alias_exists_handler(request, exc: Exception):
    """Handle AliasNotAvailable and return a 400 Bad Request JSON response."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.message,
            "code": exc.code,
            "context": exc.context,
        },
    )


async def user_already_exists_handler(request, exc: Exception):
    """Handle UserAlreadyExists and return a 409 Conflict JSON response."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": exc.message,
            "code": exc.code,
            "context": exc.context,
        },
    )


async def invalid_user_handler(request, exc: Exception):
    """Handle InvalidUser and return a 401 Unauthorized JSON response."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": exc.message,
            "code": exc.code,
            "context": exc.context,
        },
    )


async def user_forbidden_handler(request, exc: Exception):
    """Handle ForbiddenUser and return a 403 Forbidden JSON response."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "detail": exc.message,
            "code": exc.code,
            "context": exc.context,
        },
    )


async def invalid_parameter_handler(request, exc: Exception):
    """Handle InvalidParameter and return a 400 Bad Request JSON response."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.message,
            "code": exc.code,
            "context": exc.context,
        },
    )


async def url_disabled_handler(request, exc: Exception):
    """Handle URLDisabledError and return a 503 Service Unavailable JSON response."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": exc.message,
            "code": exc.code,
            "context": exc.context,
        },
    )


async def validation_exception_handler(request, exc):
    """Normalize FastAPI validation errors into the project's error payload shape."""
    logger = AppLogger().get_logger()
    logger.warning(
        "Validation failed",
        extra={
            "path": request.url.path,
            "errors": exc.errors(),
        },
    )
    for err in exc.errors():
        # Keep the final field/message pair for a compact client-facing response.
        field = ".".join(str(loc) for loc in err["loc"])
        msg = err["msg"]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "code": "VALIDATION_ERROR",
            "message": "Invalid request payload",
            "errors": exc.errors(),
        },
    )
