import os
import yaml
from pathlib import Path

CONFIG_DIR = Path.home() / ".opsautopsy"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def ensure_config_dir():
    CONFIG_DIR.mkdir(exist_ok=True)


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f) or {}


def save_config(data: dict):
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(data, f)


def set_db_url(db_url: str):
    config = load_config()
    config.setdefault("database", {})
    config["database"]["url"] = db_url
    save_config(config)


def get_db_url():
    config = load_config()
    return config.get("database", {}).get("url")
