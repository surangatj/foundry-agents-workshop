"""Lab 2 — Ground the agent in Dialog's documents (Foundry Tools + Foundry IQ).

Two ways to give an agent knowledge:

  Part A — File Search tool (built-in Foundry tool)
           Upload the 5 sample policy documents to a vector store in the project
           and let the agent search them. Works with only a model deployment.

  Part B — Foundry IQ knowledge base (agentic retrieval on Azure AI Search)
           A shared knowledge base built once by the facilitators. The agent calls
           its MCP endpoint (tool: knowledge_base_retrieve), which plans sub-queries,
           searches and returns cited answers. Set FOUNDRY_IQ_MCP_URL in .env to run it.

Run:  python -m labs.lab02_foundry_iq            (Part A)
      python -m labs.lab02_foundry_iq --iq       (Part B)
"""

import asyncio
import contextlib
import os
import sys

from agent_framework import Agent

from labs.common.config import KNOWLEDGE_DIR, agent_name, foundry_client

INSTRUCTIONS = (
    "You are Dialog Care Copilot. Answer ONLY from the knowledge tools. Quote the package code and price in LKR. "
    "If the documents do not contain the answer, say so — never guess a tariff. Reply in the customer's language. "
    "End with the source document name in brackets."
)

QUESTIONS = [
    "I'm going to Singapore for 5 days. Which roaming pass should I take and how do I activate it?",
    "My bill wasn't paid by the due date. When will my outgoing calls be barred?",
    "Can I get a new SIM over WhatsApp chat? I lost my phone.",
    "ඩේටා පැකේජ් එක ඉවර වුනාම මොකද වෙන්නේ?",  # Sinhala: what happens when my data package expires?
    "What is the price of the Netflix bundle?",  # not in the documents → the agent should say it doesn't know
]


async def build_vector_store(client) -> tuple[str, list[str]]:
    oai = client.client  # the project's OpenAI-compatible client
    store = await oai.vector_stores.create(
        name=agent_name("dialog-knowledge"), expires_after={"anchor": "last_active_at", "days": 2}
    )
    file_ids = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        uploaded = await oai.files.create(file=(path.name, path.read_bytes()), purpose="assistants")
        result = await oai.vector_stores.files.create_and_poll(vector_store_id=store.id, file_id=uploaded.id)
        if result.last_error is not None:
            raise RuntimeError(f"{path.name}: {result.last_error.message}")
        file_ids.append(uploaded.id)
        print(f"   📄 indexed {path.name}")
    return store.id, file_ids


async def main() -> None:
    client = foundry_client()
    cleanup = None

    if "--iq" in sys.argv:
        url = os.getenv("FOUNDRY_IQ_MCP_URL", "").strip()
        if not url:
            sys.exit("Set FOUNDRY_IQ_MCP_URL (and FOUNDRY_IQ_CONNECTION_ID) in .env — ask the facilitators.")
        knowledge_tool = client.get_mcp_tool(
            name="dialog_knowledge_base",
            url=url,
            allowed_tools=["knowledge_base_retrieve"],
            approval_mode="never_require",
            project_connection_id=os.getenv("FOUNDRY_IQ_CONNECTION_ID") or None,
        )
        print("Using the shared Foundry IQ knowledge base\n")
    else:
        print("Creating your vector store (≈30 s)…")
        store_id, file_ids = await build_vector_store(client)
        knowledge_tool = client.get_file_search_tool(vector_store_ids=[store_id], max_num_results=5)

        async def cleanup() -> None:
            with contextlib.suppress(Exception):
                await client.client.vector_stores.delete(vector_store_id=store_id)
            for fid in file_ids:
                with contextlib.suppress(Exception):
                    await client.client.files.delete(file_id=fid)

    agent = Agent(client=client, name="dialog-knowledge-agent", instructions=INSTRUCTIONS, tools=[knowledge_tool])
    try:
        for question in QUESTIONS:
            print(f"\n👤 {question}")
            print(f"🤖 {await agent.run(question)}")
    finally:
        if cleanup:
            await cleanup()

    # 🧪 Try it: edit data/knowledge/03_roaming_guide.md (e.g. change a price), re-run, and see the answer change.


if __name__ == "__main__":
    asyncio.run(main())
