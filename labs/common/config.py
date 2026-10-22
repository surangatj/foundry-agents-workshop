"""Shared settings for every lab.

Reads `.env` at the repo root. Required values:
    FOUNDRY_PROJECT_ENDPOINT  https://<resource>.services.ai.azure.com/api/projects/<project>
    FOUNDRY_MODEL             the chat model deployment name (e.g. gpt-5.4-mini)
    PARTICIPANT_ALIAS         your short alias, e.g. "amila-a" (keeps your agents separate from everyone else's)
"""

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"

load_dotenv(REPO_ROOT / ".env")


def require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith("<"):
        sys.exit(f"Missing {name}. Copy .env.example to .env and fill it in (see Lab 0).")
    return value


def alias() -> str:
    raw = require("PARTICIPANT_ALIAS").lower()
    return re.sub(r"[^a-z0-9-]", "-", raw).strip("-")[:20]


def agent_name(base: str) -> str:
    """Prefix agent names with your alias so 60 people can share one Foundry project."""
    return f"{alias()}-{base}"


def foundry_client():
    """A FoundryChatClient for the shared project, signed in with your `az login` identity."""
    from agent_framework.foundry import FoundryChatClient
    from azure.identity import AzureCliCredential

    return FoundryChatClient(
        project_endpoint=require("FOUNDRY_PROJECT_ENDPOINT"),
        model=require("FOUNDRY_MODEL"),
        credential=AzureCliCredential(),
    )
