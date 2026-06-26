import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import (POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD,
                             POSTGRES_PORT, POSTGRES_USER, REDIS_HOST,
                             REDIS_PASSWORD, REDIS_PORT, REDIS_USERNAME,
                             SSL_CERT_PATH)

# Redis connection (production: configure password, SSL, and connection pool if
# needed)
redis_conn = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    max_connections=10000,
)


# Database URL (production: never hardcode credentials, always use
# env/config)
DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# SQLAlchemy engine with production-ready settings
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL echo in production
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    """Dependency for getting redis session."""
    yield redis_conn
