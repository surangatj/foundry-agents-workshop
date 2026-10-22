"""Lab 6 — The continuous-improvement signal loop.

    observe (traces) → measure (evals) → diagnose (failing cases) → fix → re-measure → ship

You will publish v2 of the FAQ agent with better instructions + grounding, run the
SAME evaluation again, and compare v1 vs v2 side by side in Foundry
(Evaluations → your eval → select both runs → Compare).

In production the same loop runs automatically: a continuous-evaluation rule scores
a sample of live responses, and failing traces become the next regression test set.

Run:  python -m labs.lab06_improvement_loop          (needs EVAL_ID in .env from Lab 5)
"""

import os
import sys

from labs.common.foundry_eval import knowledge_text, project_client, publish_agent, run_eval, summarise

# ✏️  YOUR TURN: look at the failing cases from Lab 5, then improve these instructions.
V2_INSTRUCTIONS = f"""
You are "Dialog Care Copilot" for a Sri Lankan mobile operator.

Rules:
1. Answer ONLY from the KNOWLEDGE below. If it is not there, say you don't know and offer a human agent.
2. Always quote the exact package / pass CODE and the price in LKR when recommending something.
3. Reply in the same language as the customer: English, Sinhala (සිංහල) or Tamil (தமிழ்). Understand Singlish.
4. Pick the cheapest option that covers the whole trip (number of days) and the destination zone.
5. Be concise: at most 5 sentences.

KNOWLEDGE:
{knowledge_text()}
"""


def main() -> None:
    eval_id = os.getenv("EVAL_ID", "").strip()
    if not eval_id:
        sys.exit("Set EVAL_ID in .env (printed at the end of Lab 5 --eval).")
    with project_client() as project, project.get_openai_client() as oai:
        agent = publish_agent(project, V2_INSTRUCTIONS)
        print(f"📦 Published {agent.name} version {agent.version}")
        run = run_eval(oai, eval_id, agent, label=f"v{agent.version}-improved")
        print(f"\nResults for v{agent.version}:")
        summarise(oai, eval_id, run)
    print("\n➡️  In Foundry: Evaluations → open your eval → tick both runs → Compare.")
    print("   Still failing? Edit V2_INSTRUCTIONS and run again — that IS the loop.")


if __name__ == "__main__":
    main()
