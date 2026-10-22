"""Lab 5 — Observability + Evaluations.

Part A — Tracing: send OpenTelemetry traces from your agent to the Application
         Insights resource connected to the Foundry project, then inspect every
         model call, tool call and token count in Foundry (Build → Agents → Traces).

Part B — Evaluation: publish a v1 "FAQ agent" to Foundry Agent Service and run a
         cloud evaluation over 12 Sri Lankan test questions (English, Sinhala,
         Tamil, Singlish) with built-in evaluators:
           task_adherence · intent_resolution · fluency · has_expected_fact (string check)

Run:  python -m labs.lab05_observe_and_evaluate --trace
      python -m labs.lab05_observe_and_evaluate --eval
"""

import asyncio
import sys

from agent_framework import Agent

from labs.common.config import agent_name, foundry_client
from labs.common.dialog_tools import ALL_TOOLS
from labs.common.foundry_eval import create_eval, project_client, publish_agent, run_eval, summarise

# v1 is deliberately thin: no documents, no language rule. Lab 6 improves it.
V1_INSTRUCTIONS = "You are a helpful customer-care assistant for a Sri Lankan mobile operator."


async def trace_demo() -> None:
    client = foundry_client()
    # Fetches the App Insights connection string from the project and wires up OpenTelemetry.
    await client.configure_azure_monitor(enable_sensitive_data=True)
    agent = Agent(client=client, name=agent_name("traced-copilot"), tools=ALL_TOOLS,
                  instructions="You are Dialog Care Copilot. Verify customers before sharing account data.")
    for q in ["0771234501, NIC 4521 — what's on my September bill?",
              "Is there an outage in Jaffna? My fibre is down."]:
        print(f"👤 {q}\n🤖 {await agent.run(q)}\n")
    print("✅ Traces sent. In Foundry open Build → Agents → Traces (allow 2–5 minutes for ingestion).")


def eval_demo() -> None:
    with project_client() as project, project.get_openai_client() as oai:
        agent = publish_agent(project, V1_INSTRUCTIONS)
        print(f"📦 Published {agent.name} version {agent.version}")
        evaluation = create_eval(oai, name=agent_name("care-quality"))
        print(f"🧪 Evaluation id: {evaluation.id}   ← save this for Lab 6")
        run = run_eval(oai, evaluation.id, agent, label="v1-baseline")
        print(f"\nResults for v1 (status: {run.status}):")
        summarise(oai, evaluation.id, run)
        print(f"\nAdd this line to .env for Lab 6:\nEVAL_ID={evaluation.id}")


if __name__ == "__main__":
    if "--trace" in sys.argv:
        asyncio.run(trace_demo())
    else:
        eval_demo()
