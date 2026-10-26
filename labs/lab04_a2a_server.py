"""Lab 4a — Expose the Roaming agent as an A2A (Agent-to-Agent) server.

Any A2A-compatible client — another team's agent, Copilot Studio, a LangGraph or
Google ADK agent — can discover it from its Agent Card and call it over JSON-RPC.

Run (terminal 1):  python -m labs.lab04_a2a_server
Check the card:    curl http://localhost:9999/.well-known/agent-card.json
"""

import asyncio
import logging
import os
import uuid
from typing import Any

import uvicorn
from a2a.helpers import new_task_from_user_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCapabilities, AgentInterface, Part, TaskState
from agent_framework import Agent, AgentResponseUpdate
from agent_framework_hosting import AgentState
from agent_framework_hosting_a2a import AgentA2AAdapter
from starlette.applications import Starlette

from labs.common.config import foundry_client
from labs.lab03_multi_agent_handoff import ROAMING_FACTS

PORT = 9999
logger = logging.getLogger(__name__)


def public_url() -> str:
    """Advertise a reachable URL when using Codespaces or a configured tunnel."""
    codespace = os.getenv("CODESPACE_NAME", "")
    domain = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "")
    if codespace and domain:
        return f"https://{codespace}-{PORT}.{domain}/"
    return f"http://localhost:{PORT}/"


class RoamingExecutor(AgentExecutor):
    """Bridges A2A tasks to an Agent Framework agent (adapted from the Agent Framework A2A hosting sample)."""

    def __init__(self, adapter: AgentA2AAdapter[Any]) -> None:
        self.adapter = adapter

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await TaskUpdater(event_queue, context.task_id or "", context.context_id or "").cancel()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.message is None or context.context_id is None:
            raise ValueError("A2A message and context id are required")
        task = context.current_task or new_task_from_user_message(context.message)
        if context.current_task is None:
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, context.context_id)
        await updater.submit()
        try:
            await updater.start_work()
            run = self.adapter.a2a_to_run(context.message, stream=True)
            agent = await self.adapter.state.get_target()
            session_id = f"a2a:{context.context_id}"
            session = await self.adapter.state.get_or_create_session(session_id)
            stream = agent.run(run["messages"], session=session, options=run["options"], stream=True)

            artifacts: dict[tuple, str] = {}
            sent = False
            async for update in stream:
                for index, content in enumerate(update.contents):
                    # Keep each logical content item in its own artifact. A final
                    # text snapshot replaces the deltas for that item.
                    raw = content.raw_representation
                    key = (update.message_id, getattr(raw, "item_id", None),
                           getattr(raw, "content_index", index), content.type)
                    part_update = AgentResponseUpdate(role=update.role, contents=[content])
                    if parts := self.adapter.a2a_from_run(part_update):
                        append = key in artifacts and content.merge_mode != "replace"
                        artifact_id = artifacts.setdefault(key, uuid.uuid4().hex)
                        await updater.add_artifact(parts=parts, artifact_id=artifact_id, append=append)
                        sent = True
            final = await stream.get_final_response()
            if not sent and (parts := self.adapter.a2a_from_run(final)):
                await updater.update_status(state=TaskState.TASK_STATE_WORKING, message=updater.new_agent_message(parts))
            await self.adapter.state.set_session(session_id, session)
            await updater.complete()
        except Exception:
            logger.exception("Roaming agent failed")
            await updater.update_status(
                state=TaskState.TASK_STATE_FAILED, message=updater.new_agent_message([Part(text="Agent failed.")])
            )


def main() -> None:
    agent = Agent(
        client=foundry_client(),
        name="Dialog Roaming Agent",
        description="Recommends international roaming passes and explains roaming rates for Sri Lankan travellers.",
        instructions=f"You are a roaming specialist for a Sri Lankan mobile operator. Amounts in LKR. {ROAMING_FACTS}",
    )
    adapter = AgentA2AAdapter(
        AgentState(agent),
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[AgentInterface(url=public_url(), protocol_binding="JSONRPC")],
    )
    card = asyncio.run(adapter.get_card())
    handler = DefaultRequestHandler(agent_executor=RoamingExecutor(adapter), task_store=InMemoryTaskStore(), agent_card=card)
    app = Starlette(routes=[*create_agent_card_routes(card), *create_jsonrpc_routes(handler, "/")])
    print(f"🛰️  Roaming agent listening on http://localhost:{PORT}  (Ctrl+C to stop)")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
