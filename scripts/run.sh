find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} +

fastapi dev app/main.py