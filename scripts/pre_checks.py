import os
import sys

from app.core.config import SSL_CERT_PATH
from app.core.db import Base, engine
from app.core.logging import AppLogger
from app.models import *

logger = AppLogger().get_logger()


def init_db():
    """Create all database tables defined in SQLAlchemy metadata if they do not already exist."""
    try:
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created!")
    except Exception as e:
        sys.exit(1)
        logger.error(f"Error syncing click counts: {e}")


def check_ssl_cert():
    """
    Ensure SSL certificate exists before app starts.
    Fail fast if missing.
    """
    if not SSL_CERT_PATH:
        logger.error("SSL_CERT_PATH is not configured.")
        sys.exit(1)
    if not os.path.exists(SSL_CERT_PATH):
        logger.error(f"SSL certificate not found at: {SSL_CERT_PATH}")
        sys.exit(1)
    logger.info(f"SSL certificate found: {SSL_CERT_PATH}")
