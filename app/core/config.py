"""Centralized application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
env_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=env_path)

BASEDIR = os.path.dirname(os.path.abspath(__file__))
SSL_CERT_PATH = os.path.join(BASEDIR, "certs", "global-bundle.pem")
IPO_CERT_PATH = os.path.join(BASEDIR, "certs", "ipinfo.io.crt")

# PostgreSQL configuration
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
#  Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Scurity Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


# Application messages
URL_SHORTENED_SUCCESSFULLY = "URL Shortened Successfully"
URL_DOESNOT_EXIST = "Not Found"
USER_CREATION_SUCCESSFUL = "User Creation Successful"
USER_FORBIDDEN_ERROR = "Unauthorised to perform this operation"
# Field names for database lookups and responses
PORT = 8000
DOMAIN = f"http://localhost:{PORT}/"
SYNC_STATUS = False
RESERVED_ALIASES = {"admin", "login", "signup", "dashboard"}

# Scopes
SIGNUP = "signup"
LOGIN = "login"
CREATE = "create"
PATCH = "patch"
INFO = "info"
ANALYTICS = "analytics"
REGSITER = "register"
DELETE = "delete"
REDIRECT = "redirect"
USERINFO = "userinfo"
USER = "user"
IP = "ip"

# Action keys
URL = "url"
PATCHING = "patching"
DELETED = "deleted"
USER_URLS = "user_urls"
GEO = "geo"
USER_AGENT = "user_agent"

# Batch Size
BULK_DELETE_BATCH_SIZE = 20000
BULK_PATCH_BATCH_SIZE = 20000
BULK_CREATE_BATCH_SIZE = 20000

# Kafka Config
BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS")
SECURITY_PROTOCOL = os.getenv("SECURITY_PROTOCOL")
SASL_MECHANISMS = os.getenv("SASL_MECHANISMS")
SASL_USERNAME = os.getenv("SASL_USERNAME")
SASL_PASSWORD = os.getenv("SASL_PASSWORD")
SESSION_TIMEOUT_MS = os.getenv("SESSION_TIMEOUT_MS")
CLIENT_ID = os.getenv("CLIENT_ID")
KAFKA_CONFIG = {
    "bootstrap.servers": BOOTSTRAP_SERVERS,
    "security.protocol": SECURITY_PROTOCOL,
    "client.id": CLIENT_ID,
}
KAFKA_OFFSET="earliest"
KAFKA_LOGGER="kafka"


# Topics
ANALYTICS_DLQ = "analytics_dlq"
TOPICS = "redirect_queue"

# Consumers
ANALYTICS_CONSUMER = "analytics-consumer"
ARCHIVAL_CONSUMER = "archival-consumer"
CLICK_COUNT_CONSUMER = "click-count-consumer"

# Static IP
MY_IP = ["167.103.76.80","167.103.26.249"]
GEO_IP_TTL = 86400
GEO_DETAILS_API = "https://ipinfo.io/{ip}/json"

# Analytics Dashboard
TOP_URLS_LIMIT = 1
LATEST_URLS_LIMIT = 2
CLICK_TREND_LIMIT = 5
DELTA_FOR_ONE_DAY = 1
DELTA_FOR_ONE_WEEK = 7
DELTA_FOR_ONE_MONTH = 7
