"""Project configuration loading from project.yaml and .env."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

MARKETING_DIR = ".marketing"
PROJECT_FILE = "project.yaml"
DB_FILE = "campaign.db"


def find_project_root() -> Path:
    """Walk up from cwd to find project.yaml."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / PROJECT_FILE).exists():
            return parent
    return cwd


def get_marketing_dir() -> Path:
    root = find_project_root()
    d = root / MARKETING_DIR
    d.mkdir(exist_ok=True)
    return d


def get_db_path() -> Path:
    return get_marketing_dir() / DB_FILE


def load_project_config() -> dict:
    """Load project.yaml from project root."""
    root = find_project_root()
    config_path = root / PROJECT_FILE
    if not config_path.exists():
        raise FileNotFoundError(f"No {PROJECT_FILE} found. Run 'marketing init' first.")
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_env() -> dict:
    """Load .env credentials."""
    load_dotenv()
    return {
        "reddit": {
            "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
            "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
            "username": os.getenv("REDDIT_USERNAME", ""),
            "password": os.getenv("REDDIT_PASSWORD", ""),
            "user_agent": os.getenv("REDDIT_USER_AGENT", "campaign-manager:v0.1"),
        },
        "devto": {
            "api_key": os.getenv("DEVTO_API_KEY", ""),
        },
    }
