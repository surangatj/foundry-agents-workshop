"""Lab 4b — Call the remote Roaming agent over A2A from the Care Copilot.

1. Discover the remote agent from its Agent Card (/.well-known/agent-card.json)
2. Call it directly as an A2AAgent
3. Wrap it as a tool so the Care Copilot decides when to delegate to it

Run (terminal 2, while lab04_a2a_server is running):
      python -m labs.lab04_a2a_client
Pair up: set A2A_AGENT_HOST to your neighbour's forwarded Codespaces URL to call THEIR agent.
"""

import asyncio
import os

import httpx
from a2a.client import A2ACardResolver
from agent_framework import Agent
from agent_framework.a2a import A2AAgent

from labs.common.config import foundry_client
from labs.common.dialog_tools import ALL_TOOLS


async def main() -> None:
    host = os.getenv("A2A_AGENT_HOST", "").strip().rstrip("/") or "http://localhost:9999"

    async with httpx.AsyncClient(timeout=60.0) as http:
        card = await A2ACardResolver(httpx_client=http, base_url=host).get_agent_card()
    # The discovered card may advertise localhost behind a forwarded port.
    # Route its JSON-RPC interface through the host the participant selected.
    for interface in card.supported_interfaces:
        if interface.protocol_binding == "JSONRPC":
            interface.url = host + "/"
    print(f"🔎 Discovered: {card.name} — {card.description}")

    async with A2AAgent(name=card.name, description=card.description, agent_card=card, url=host) as roaming:
        # Direct call
        reply = await roaming.run("Which pass for 10 days in Dubai?")
        print(f"\n🛰️  Direct A2A call → {reply.text}\n")

        # As a tool: the local Care Copilot delegates roaming questions to the remote agent
        copilot = Agent(
            client=foundry_client(),
            name="dialog-care-copilot",
            instructions=(
                "You are Dialog Care Copilot. For ANY roaming or travel question, call the roaming specialist tool. "
                "For account questions use your own tools and verify the customer first."
            ),
            tools=[*ALL_TOOLS, roaming.as_tool(name="roaming_specialist", description=card.description or "")],
        )
        question = "I'm 0774567804, NIC 1123. I'm flying to Singapore again next month — how do I avoid last month's roaming charges?"
        print(f"👤 {question}")
        print(f"🤖 {await copilot.run(question)}")


if __name__ == "__main__":
    asyncio.run(main())
