import json
from pathlib import Path

config_path = Path(__file__).parent / "settings.example.json"

if config_path.exists():
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {"API_ENDPOINT": "https://api.twitter-simulator.local/user", "TIMEOUT": 5}

API_ENDPOINT = data.get("API_ENDPOINT")
TIMEOUT = data.get("TIMEOUT")