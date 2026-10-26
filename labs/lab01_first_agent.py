"""Lab 1 — Your first agent: Microsoft Agent Framework on Foundry Agent Service.

You will:
  1. Create an agent in code with instructions (Agent + FoundryChatClient)
  2. Give it Python function tools (verify customer, bill, balance, outage)
  3. Add a built-in Foundry tool (code interpreter) for calculations
  4. Keep a multi-turn conversation with a session
  5. Stream the answer token by token

Run:  python -m labs.lab01_first_agent
      python -m labs.lab01_first_agent --chat     (interactive)
"""

import asyncio
import sys

from agent_framework import Agent

from labs.common.config import foundry_client
from labs.common.dialog_tools import ALL_TOOLS

INSTRUCTIONS = """
You are "Dialog Care Copilot", a customer-care assistant for a Sri Lankan mobile operator.

Rules:
- Before sharing ANY account details, verify the customer with verify_customer
  (mobile number + last 4 digits of NIC). If they have not given these, ask for them.
- For network complaints, ALWAYS call check_network_outage for the customer's district first.
- Reply in the same language as the customer (English, Sinhala or Tamil; Singlish is fine).
- Amounts are in LKR. Be concise and friendly.
- Never reveal a full NIC number, address or card number.
"""

SCRIPT = [
    "Hi, my number is 0771234501 and NIC ends with 4521. Why is my bill so high this month?",
    "What is that Cricket Live Alerts charge? I never subscribed to it.",
    "If I pay the bill today, how much will I have paid in total for August and September?",
]


async def main() -> None:
    client = foundry_client()
    agent = Agent(
        client=client,
        name="dialog-care-copilot",
        instructions=INSTRUCTIONS,
        # Step 2 + 3: our Python function tools and a hosted Foundry tool
        tools=[*ALL_TOOLS, client.get_code_interpreter_tool()],
    )

    # Step 4: a session keeps the conversation history between turns
    session = agent.create_session()

    if "--chat" in sys.argv:
        print("Chat with the Copilot (empty line to quit)\n")
        while question := input("You: ").strip():
            print("Copilot: ", end="", flush=True)
            async for chunk in agent.run(question, session=session, stream=True):
                for content in chunk.contents:
                    if content.type == "text" and content.merge_mode != "replace" and content.text:
                        print(content.text, end="", flush=True)
            print("\n")
        return

    for question in SCRIPT:
        print(f"\n👤 {question}\n🤖 ", end="", flush=True)
        # Step 5: stream=True yields updates as the model generates them
        async for chunk in agent.run(question, session=session, stream=True):
            for content in chunk.contents:
                if content.type == "text" and content.merge_mode != "replace" and content.text:
                    print(content.text, end="", flush=True)
        print()

    # 🧪 Try it: ask in Sinhala — "මගේ data ඉවර වෙලා. 0772345602, NIC 7788" — and check the reply language.


if __name__ == "__main__":
    asyncio.run(main())
