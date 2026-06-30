from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.exception_handlers import (alias_exists_handler,
                                         invalid_parameter_handler,
                                         invalid_user_handler,
                                         url_deleted_handler,
                                         url_disabled_handler,
                                         url_expired_handler,
                                         url_not_found_handler,
                                         user_already_exists_handler,
                                         user_forbidden_handler,
                                         validation_exception_handler)
from app.core.exceptions import (AliasNotAvailable, ForbiddenUser,
                                 InvalidParameter, InvalidUser,
                                 RecordNotFoundError, URLDeletedError,
                                 URLDisabledError, URLExpiredError,
                                 UserAlreadyExists)
from app.core.logging import AppLogger
from app.routes.admin import admin_router, inspect_router
from app.routes.analytics import analytics_router
from app.routes.auth import auth_router
from app.routes.celery import celery_router
from app.routes.health import health_check_router
from app.routes.kakfa import kafka_router
from app.routes.redirect import redirect_router
from app.routes.url import url_router
from app.utils.request_context import RequestContextMiddleware
from scripts.pre_checks import init_db

logger = AppLogger().get_logger()

app = FastAPI(
    title="URL Shortener API",
    description="A simple URL shortener API built with FastAPI",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)

app.include_router(router=health_check_router)
app.include_router(router=redirect_router)
app.include_router(router=analytics_router)
app.include_router(router=auth_router)
app.include_router(router=url_router)
app.include_router(router=celery_router)
app.include_router(router=kafka_router)
app.include_router(router=inspect_router)
app.include_router(router=admin_router)


@app.on_event("startup")
def startup():
    """Initialize the database and launch the background click worker on app startup."""
    logger.info("Application startup sequence started")
    init_db()


app.add_exception_handler(RecordNotFoundError, url_not_found_handler)
app.add_exception_handler(URLExpiredError, url_expired_handler)
app.add_exception_handler(URLDeletedError, url_deleted_handler)
app.add_exception_handler(AliasNotAvailable, alias_exists_handler)
app.add_exception_handler(UserAlreadyExists, user_already_exists_handler)
app.add_exception_handler(InvalidUser, invalid_user_handler)
app.add_exception_handler(ForbiddenUser, user_forbidden_handler)
app.add_exception_handler(InvalidParameter, invalid_parameter_handler)
app.add_exception_handler(URLDisabledError, url_disabled_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
