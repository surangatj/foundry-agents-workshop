"""Lab 0 — Check that your environment can reach the shared Foundry project.

Run:  python -m labs.lab00_check_setup
"""

import asyncio
import shutil
import subprocess
import sys

from labs.common.config import alias, foundry_client, require


def check(label: str, ok: bool, hint: str = "") -> bool:
    print(f"  {'✅' if ok else '❌'} {label}" + (f"\n     → {hint}" if not ok and hint else ""))
    return ok


async def main() -> None:
    print("Dialog Care Copilot — environment check\n")
    ok = check(f"Python {sys.version.split()[0]}", sys.version_info >= (3, 11), "Use Python 3.11–3.13.")
    
    az_path = shutil.which("az")
    ok &= check(
        "Azure CLI installed",
        az_path is not None,
        "Install the Azure CLI, then restart your terminal.",
    )

    signed_in = (
        az_path is not None
        and subprocess.run(
            [az_path, "account", "show", "-o", "none"],
            capture_output=True,
        ).returncode == 0
    )
    
    ok &= check("Signed in with az login", signed_in, "Run: az login --use-device-code")

    require("FOUNDRY_PROJECT_ENDPOINT")
    require("FOUNDRY_MODEL")
    print(f"  ✅ .env loaded — your alias is '{alias()}'")
    if not ok:
        sys.exit("\nFix the items above, then run this check again.")

    print("\nCalling your model deployment through Foundry…")
    from agent_framework import Agent

    agent = Agent(client=foundry_client(), instructions="Reply in one short sentence.")
    try:
        reply = await agent.run("Say 'Ayubowan' and tell me which model you are.")
    except Exception as exc:  # noqa: BLE001 — show any auth/RBAC/network error plainly
        sys.exit(f"  ❌ Foundry call failed: {exc}\n     → Check the endpoint, the deployment name and your "
                f"'Azure AI User' role on the project (ask Damika or Rusiru).")
    print(f"  ✅ {reply.text}\n\nYou're ready for Lab 1 🎉")


if __name__ == "__main__":
    asyncio.run(main())
