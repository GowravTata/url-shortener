"""
Seed script for bulk URL creation with venv setup and robust error handling.
"""
import argparse
import os
import sys
import subprocess
import json

TOPICS = [
    "analytics-consumer",
    "archival-consumer",
    "click-count-consumer"
]

# ----------------------------
# Virtual Environment Setup
# ----------------------------
def setup_venv(venv_dir="venv"):
    """Create a virtual environment if not exists and install requests."""
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        print("✅ Virtual environment created at", venv_dir)

    pip_path = os.path.join(venv_dir, "Scripts" if os.name == "nt" else "bin", "pip")

    print("Installing required packages inside venv...")
    subprocess.check_call([pip_path, "install", "--upgrade", "pip"])
    subprocess.check_call([pip_path, "install", "requests"])
    print("✅ Dependencies installed in venv")

    return os.path.join(venv_dir, "Scripts" if os.name == "nt" else "bin", "python")


# ----------------------------
# Import requests from venv
# ----------------------------
def import_requests():
    try:
        import requests
        return requests
    except ImportError:
        raise RuntimeError("requests not available — ensure venv setup ran correctly.")


# ----------------------------
# Configuration
# ----------------------------
URL = "http://amazon.com"
PORT = 8000

def configure_endpoints(domain: str):
    global ENDPOINTS

    ENDPOINTS = {
        "register_user": f"{domain}/v1/auth/register_user",
        "login": f"{domain}/v1/auth/login-json",
        "bulk_create": f"{domain}/v1/urls/bulk",
        "create_kafka_topic": f"{domain}/v1/kafka/topics/",
    }

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

CREDENTIALS = [
    {"email": "gowravsaitata@fastapi.com", "password": "secretpassword"},
    {"email": "gowravtata@fastapi.com", "password": "secretpassword"},
    {"email": "bhargavtata@fastapi.com", "password": "secretpassword"},
]


# ----------------------------
# Helper Functions
# ----------------------------
def generate_create_data(url: str, limit: int) -> dict:
    return {
        "urls": [
            {"original_url": url, "custom_alias": f"az{i}"}
            for i in range(1, limit + 1)
        ]
    }


def send_post_data(url: str, headers: dict, payload: dict, context: str = "") -> dict:
    try:
        response = requests.post(
            url=url, headers=headers, data=json.dumps(payload), timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"[{context}] Request failed: {e}")

    try:
        return response.json()
    except ValueError:
        raise RuntimeError(f"[{context}] Response not JSON: {response.text}")


def try_create_user(credentials: dict) -> bool:
    """Attempt to create a user, return True if successful, False otherwise."""
    try:
        send_post_data(
            ENDPOINTS["register_user"], HEADERS, credentials, context="create_user"
        )
        print(f"✅ User created: {credentials['email']}")
        return True
    except Exception as e:
        print(f"⚠️ Failed to create user {credentials['email']}: {e}")
        return False


def get_token(credentials: dict) -> str:
    """Login and retrieve JWT access token for given credentials."""
    output = send_post_data(
        ENDPOINTS["login"], HEADERS, credentials, context="get_token"
    )
    token = output.get("access_token")
    if not token:
        raise RuntimeError(f"[get_token] No access_token in response: {output}")
    return token


def create_kafka_topics():
    """Create the required Kafka topics."""
    print("Creating Kafka topics...")
    for topic in TOPICS:
        try:
            response = requests.post(
                url=ENDPOINTS["create_kafka_topic"],
                params={
                    "topic": topic,
                    "partitions": 1,
                    "replication_factor": 1,
                },
                headers=HEADERS,
                timeout=10,
            )
            response.raise_for_status()
            print(f"✅ Topic created: {topic}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Failed to create topic '{topic}': {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Seed the URL Shortener application."
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="Hostname or IP address of the URL Shortener service.",
    )

    return parser.parse_args()

def load_data_into_db(limit: int):
    # Step 0: Create Kafka Topics
    create_kafka_topics()
    # Step 1: Find a usable user
    chosen_user = None
    for creds in CREDENTIALS:
        if try_create_user(creds):
            chosen_user = creds
            break

    if not chosen_user:
        raise RuntimeError("❌ No user could be created successfully.")

    # Step 2: Generate payload
    print("Generating payload...")
    payload = generate_create_data(url=URL, limit=limit)

    # Step 3: Fetch token
    print("Fetching token...")
    token = get_token(chosen_user)
    HEADERS["Authorization"] = f"Bearer {token}"

    # Step 4: Bulk insert
    print("Sending bulk URL creation request...")
    result = send_post_data(
        ENDPOINTS["bulk_create"], HEADERS, payload, context="bulk_create"
    )
    print("Bulk create response:", result)

    return "Data Loaded Successfully"


# ----------------------------
# Script Entry Point
# ----------------------------
if __name__ == "__main__":
    python_path = setup_venv()
    requests = import_requests()
    args = parse_arguments()
    DOMAIN = f"http://{args.host}:8000"

    configure_endpoints(DOMAIN)

    try:
        print(load_data_into_db(limit=25))
    except Exception as e:
        print("❌ Seed script failed:", e)
