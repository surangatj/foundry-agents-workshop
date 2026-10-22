"""Lab 3 — Multi-agent workflow: triage → specialists (handoff orchestration).

A triage agent reads the customer's message and hands off to the right specialist:
  • billing-agent   — bills, credits, prepaid balance
  • network-agent   — outages, data/fibre faults, tickets
  • roaming-agent   — travel, roaming passes and rates

Specialists can hand control back or to each other. HandoffBuilder creates the
handoff tools for you; you only write the agents.

Run:  python -m labs.lab03_multi_agent_handoff
"""

import asyncio
from typing import cast

from agent_framework import Agent, AgentResponse, WorkflowEvent
from agent_framework.orchestrations import HandoffAgentUserRequest, HandoffBuilder

from labs.common.config import foundry_client
from labs.common.dialog_tools import BILLING_TOOLS, NETWORK_TOOLS

COMMON = (
    "You work for a Sri Lankan mobile operator's customer care team. Reply in the customer's language "
    "(English, Sinhala or Tamil). Verify the customer (mobile + last 4 NIC digits) before sharing account data. "
    "Amounts are in LKR. Be concise."
)

ROAMING_FACTS = (
    "Roaming passes: RM-SA-3 South Asia (India, Maldives, Bangladesh, Nepal, Pakistan) LKR 1,490 for 3 GB/3 days; "
    "RM-SA-7 LKR 2,990 for 8 GB/7 days; RM-ASIA-7 (Singapore, Malaysia, Thailand, Indonesia, Vietnam, UAE, Qatar, "
    "Saudi Arabia, Oman, Kuwait) LKR 3,990 for 6 GB/7 days; RM-ASIA-30 LKR 8,990 for 20 GB/30 days; "
    "RM-WORLD-7 LKR 5,990 for 4 GB/7 days; RM-ME-WORKER LKR 1,990/30 days. Activate with #126#. "
    "Postpaid customers must activate roaming with #125# before travelling."
)


def create_agents() -> tuple[Agent, Agent, Agent, Agent]:
    client = foundry_client()
    triage = Agent(
        client=client,
        name="triage_agent",
        instructions=(
            f"{COMMON} You are the front desk. Work out what the customer needs and hand off to "
            "billing_agent (bills, charges, credits, balance), network_agent (no signal, slow data, fibre, outages) "
            "or roaming_agent (travel abroad). Do not answer specialist questions yourself."
        ),
        require_per_service_call_history_persistence=True,
    )
    billing = Agent(
        client=client,
        name="billing_agent",
        instructions=(
            f"{COMMON} You handle bills, disputes and credits. You may approve credits up to LKR 2,000; above "
            "that raise a BILLING_ESCALATION ticket. Unknowingly activated VAS subscriptions are refunded."
        ),
        tools=BILLING_TOOLS,
        require_per_service_call_history_persistence=True,
    )
    network = Agent(
        client=client,
        name="network_agent",
        instructions=(
            f"{COMMON} You fix connectivity problems. ALWAYS check_network_outage for the district first. "
            "If there is an outage, give the ETA and do not raise a ticket. Otherwise troubleshoot, then raise a ticket."
        ),
        tools=NETWORK_TOOLS,
        require_per_service_call_history_persistence=True,
    )
    roaming = Agent(
        client=client,
        name="roaming_agent",
        instructions=f"{COMMON} You help customers who are travelling. {ROAMING_FACTS}",
        require_per_service_call_history_persistence=True,
    )
    return triage, billing, network, roaming


def show(events: list[WorkflowEvent]) -> list[WorkflowEvent[HandoffAgentUserRequest]]:
    """Print what happened and collect requests for the next user message."""
    pending: list[WorkflowEvent[HandoffAgentUserRequest]] = []
    for event in events:
        if event.type == "handoff_sent":
            print(f"   🔀 handoff: {event.data.source} → {event.data.target}")
        elif event.type == "output" and isinstance(event.data, AgentResponse):
            for message in event.data.messages:
                if message.text:
                    print(f"🤖 [{message.author_name or message.role}] {message.text}")
        elif event.type == "request_info" and isinstance(event.data, HandoffAgentUserRequest):
            for message in event.data.agent_response.messages:
                if message.text:
                    print(f"🤖 [{message.author_name or message.role}] {message.text}")
            pending.append(cast(WorkflowEvent[HandoffAgentUserRequest], event))
    return pending


async def main() -> None:
    triage, billing, network, roaming = create_agents()
    workflow = (
        HandoffBuilder(
            name="dialog_care_handoff",
            participants=[triage, billing, network, roaming],
            termination_condition=lambda conversation: (
                len(conversation) > 0 and "thank" in (conversation[-1].text or "").lower()
                and conversation[-1].role == "user"
            ),
        )
        .with_start_agent(triage)
        .build()
    )

    script = [
        "My 4G has not been working since morning in Peradeniya. Number 0772345602, NIC 7788.",
        "OK. Also I'm going to Singapore next week for 5 days — what is the best data option?",
        "Thank you!",
    ]

    print(f"👤 {script[0]}")
    pending = show([event async for event in workflow.run(script[0], stream=True)])
    for reply in script[1:]:
        if not pending:
            break
        print(f"\n👤 {reply}")
        responses = {req.request_id: HandoffAgentUserRequest.create_response(reply) for req in pending}
        pending = show(await workflow.run(responses=responses))

    # 🧪 Try it: change the script to a billing dispute in Tamil and watch which agent takes over.


if __name__ == "__main__":
    asyncio.run(main())

