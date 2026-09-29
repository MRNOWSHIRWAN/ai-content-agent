"""Configuration loading: .env file + config.yaml.

Keeps every tunable in one place so the rest of the code stays clean.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "config.yaml"
DEFAULT_ENV = PROJECT_ROOT / ".env"


def load_env_file(path: Path = DEFAULT_ENV) -> None:
    """Load KEY=VALUE lines from a .env file, if it exists.

    Existing environment variables always win over the file.
    """
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_config(path: str | Path | None = None) -> dict:
    """Read config.yaml and return it as a dict."""
    config_path = Path(path) if path else DEFAULT_CONFIG
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def get_gemini_key() -> str | None:
    """Return the Gemini API key from the environment (or .env), if set."""
    load_env_file()
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    return key or None
