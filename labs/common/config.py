"""Shared settings for every lab.

Reads `.env` at the repo root. Required values:
    FOUNDRY_PROJECT_ENDPOINT  https://<resource>.services.ai.azure.com/api/projects/<project>
    FOUNDRY_MODEL             the chat model deployment name (e.g. gpt-5.4-mini)
    PARTICIPANT_ALIAS         your short alias, e.g. "amila-a" (keeps your agents separate from everyone else's)

Optional: FOUNDRY_API_KEY selects API-key authentication without Azure CLI.
Leave it empty to keep the original Azure CLI sign-in flow.
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


def api_key() -> str | None:
    """Return a configured resource key, without displaying it."""
    if os.getenv("FOUNDRY_API_KEY", "").strip():
        return require("FOUNDRY_API_KEY")
    return None


def project_client(*, asynchronous: bool = False):
    """Use the same authentication for project APIs and OpenAI-compatible APIs."""
    if asynchronous:
        from azure.ai.projects.aio import AIProjectClient
    else:
        from azure.ai.projects import AIProjectClient

    key = api_key()
    endpoint = require("FOUNDRY_PROJECT_ENDPOINT")
    if key is None:
        if asynchronous:
            from azure.identity.aio import AzureCliCredential
        else:
            from azure.identity import AzureCliCredential
        return AIProjectClient(endpoint=endpoint, credential=AzureCliCredential())

    from azure.core.credentials import AzureKeyCredential
    from azure.core.pipeline.policies import AzureKeyCredentialPolicy
    import httpx2
    from openai import DefaultAsyncHttpxClient, DefaultHttpxClient

    class ApiKeyAuth(httpx2.Auth):
        def auth_flow(self, request):
            # OpenAI validates bearer credentials before its HTTP transport runs.
            # Send the Foundry resource key only in its documented api-key header.
            request.headers.pop("Authorization", None)
            request.headers["api-key"] = key
            yield request

    # azure-ai-projects 2.7 defaults to Entra tokens, including in
    # get_openai_client(). Override both public authentication hooks.
    class ApiKeyProjectClient(AIProjectClient):
        def get_openai_client(self, **kwargs):
            http_client = kwargs.get("http_client")
            if http_client is None:
                http_client = DefaultAsyncHttpxClient() if asynchronous else DefaultHttpxClient()
            http_client.auth = ApiKeyAuth()
            kwargs["http_client"] = http_client
            kwargs["api_key"] = key
            return super().get_openai_client(**kwargs)

    credential = AzureKeyCredential(key)
    return ApiKeyProjectClient(
        endpoint=endpoint,
        credential=credential,
        authentication_policy=AzureKeyCredentialPolicy(credential, "api-key"),
    )


def foundry_client():
    """Use FOUNDRY_API_KEY when set, otherwise the original az login identity."""
    from agent_framework.foundry import FoundryChatClient
    if api_key() is not None:
        return FoundryChatClient(project_client=project_client(asynchronous=True), model=require("FOUNDRY_MODEL"))

    from azure.identity import AzureCliCredential

    return FoundryChatClient(
        project_endpoint=require("FOUNDRY_PROJECT_ENDPOINT"),
        model=require("FOUNDRY_MODEL"),
        credential=AzureCliCredential(),
    )
