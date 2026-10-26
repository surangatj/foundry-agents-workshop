"""Lab 0 — Check that your environment can reach the shared Foundry project.

Run:  python -m labs.lab00_check_setup
"""

import asyncio
import shutil
import subprocess
import sys

from labs.common.config import alias, api_key, foundry_client, require


def check(label: str, ok: bool, hint: str = "") -> bool:
    print(f"  {'✅' if ok else '❌'} {label}" + (f"\n     → {hint}" if not ok and hint else ""))
    return ok


async def main() -> None:
    print("Dialog Care Copilot — environment check\n")
    ok = check(f"Python {sys.version.split()[0]}", sys.version_info >= (3, 11), "Use Python 3.11–3.13.")
    
    using_key = api_key() is not None
    if using_key:
        print("  ✅ API key configured — Azure CLI and az login are not required")
    else:
        az_path = shutil.which("az")
        ok &= check(
            "Azure CLI installed",
            az_path is not None,
            "Set FOUNDRY_API_KEY in .env, or install the Azure CLI and restart your terminal.",
        )
        signed_in = (
            az_path is not None
            and subprocess.run(
                [az_path, "account", "show", "-o", "none"],
                capture_output=True,
            ).returncode == 0
        )
        ok &= check("Signed in with az login", signed_in, "Run: az login --use-device-code, or set FOUNDRY_API_KEY.")

    require("FOUNDRY_PROJECT_ENDPOINT")
    require("FOUNDRY_MODEL")
    print(f"  ✅ .env loaded — your alias is '{alias()}'")
    if not ok:
        sys.exit("\nFix the items above, then run this check again.")

    print("\nCalling your model deployment through Foundry…")
    from agent_framework import Agent

    try:
        agent = Agent(client=foundry_client(), instructions="Reply in one short sentence.")
        reply = await agent.run("Say 'Ayubowan' and tell me which model you are.")
    except Exception as exc:  # noqa: BLE001 — show any auth/RBAC/network error plainly
        hint = (
            "Check that the key belongs to this Foundry resource and API-key access is enabled for this endpoint."
            if using_key else "Check your 'Azure AI User' role on the project."
        )
        sys.exit(f"  ❌ Foundry call failed: {exc}\n     → Check the endpoint and deployment name. {hint} "
                 "Ask Damika or Rusiru.")
    print(f"  ✅ {reply.text}\n\nYou're ready for Lab 1 🎉")


if __name__ == "__main__":
    asyncio.run(main())
