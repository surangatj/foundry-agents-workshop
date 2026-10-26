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
    paths = sorted(KNOWLEDGE_DIR.glob("*.md"))
    if not paths:
        raise ValueError(f"No knowledge documents found in {KNOWLEDGE_DIR}.")
    store = await oai.vector_stores.create(
        name=agent_name("dialog-knowledge"), expires_after={"anchor": "last_active_at", "days": 2}
    )
    file_ids = []
    try:
        for path in paths:
            uploaded = await oai.files.create(file=(path.name, path.read_bytes()), purpose="assistants")
            file_ids.append(uploaded.id)  # Track the upload before indexing can fail.
            result = await oai.vector_stores.files.create_and_poll(vector_store_id=store.id, file_id=uploaded.id)
            if result.status != "completed" or result.last_error is not None:
                raise RuntimeError(f"{path.name}: {result.last_error or result.status}")
            print(f"   📄 indexed {path.name}")
    except BaseException:
        await delete_vector_store(client, store.id, file_ids)
        raise
    return store.id, file_ids


async def delete_vector_store(client, store_id: str, file_ids: list[str]) -> None:
    try:
        await client.client.vector_stores.delete(vector_store_id=store_id)
    except Exception as exc:
        print(f"Cleanup warning: could not delete vector store {store_id}: {exc}")
    for fid in file_ids:
        try:
            await client.client.files.delete(file_id=fid)
        except Exception as exc:
            print(f"Cleanup warning: could not delete file {fid}: {exc}")


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
        async def cleanup() -> None:
            await delete_vector_store(client, store_id, file_ids)

    try:
        if "--iq" not in sys.argv:
            knowledge_tool = client.get_file_search_tool(vector_store_ids=[store_id], max_num_results=5)
        agent = Agent(client=client, name="dialog-knowledge-agent", instructions=INSTRUCTIONS, tools=[knowledge_tool])
        for question in QUESTIONS:
            print(f"\n👤 {question}")
            print(f"🤖 {await agent.run(question)}")
    finally:
        if cleanup:
            await cleanup()

    # 🧪 Try it: edit data/knowledge/03_roaming_guide.md (e.g. change a price), re-run, and see the answer change.


if __name__ == "__main__":
    asyncio.run(main())
