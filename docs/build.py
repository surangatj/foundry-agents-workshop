"""Builds the workshop website (GitHub Pages serves /docs).

Edit the content below, then run:  python docs/build.py
"""

from html import escape
from pathlib import Path

OUT = Path(__file__).parent
REPO = "https://github.com/surangatj/foundry-agents-workshop"
CODESPACE = "https://codespaces.new/surangatj/foundry-agents-workshop?quickstart=1"
DATE = "Monday 26 October 2026 · 09:00–13:30 Sri Lanka time"


def code(text: str, label: str = "") -> str:
    lbl = f'<div class="lbl">{escape(label)}</div>' if label else ""
    return f'<div class="code">{lbl}<pre><code>{escape(text.strip())}</code></pre></div>'


def note(kind: str, title: str, body: str) -> str:
    return f'<div class="note {kind}"><b>{title}</b> {body}</div>'


BRAND = ('<span class="brand"><span class="d">Dialog</span><span class="x">×</span>'
         '<span class="f">Microsoft Foundry</span><span class="by">· delivered by hONE</span></span>')


def page(title: str, h1: str, lead: str, body: str, depth: int = 1, chips: list[str] | None = None) -> str:
    up = "../" * depth
    chip_html = "".join(f'<span class="chip">{escape(c)}</span>' for c in chips or [])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><link rel="stylesheet" href="{up}assets/site.css"></head>
<body>
<header class="top"><div class="in"><a class="back" href="{up}home.html">← Workshop home</a>
<div style="margin-top:10px">{BRAND}</div>
<h1>{h1}</h1><p>{lead}</p><div class="chips">{chip_html}</div></div></header>
<main class="wrap">{body}</main>
<footer>Dialog × Microsoft Foundry agents workshop · delivered by hONE · all customer data and tariffs are fictional sample data ·
<a href="{REPO}">source on GitHub</a></footer>
<script src="{up}assets/site.js"></script>
</body></html>
"""


# --------------------------------------------------------------------------- labs
LABS = [
    dict(
        slug="lab0", n=0, title="Set up your environment", minutes=10, kind="core",
        topics=["Setup"],
        recap="Everything runs in a <b>GitHub Codespace</b> — VS Code in your browser with Python 3.13, the Azure CLI "
              "and all packages preinstalled. You sign in with your Dialog account and point the code at the shared "
              "Foundry project.",
        goals=["Open the workshop in a Codespace", "Sign in to Azure", "Connect to the Foundry project and get a reply from the model"],
        steps=[
            ("Open the Codespace",
             f'<p>Click the button. A browser VS Code opens and installs everything (about 2 minutes the first time).</p>'
             f'<div class="ctas"><a class="cta" href="{CODESPACE}">Open in GitHub Codespaces ↗</a></div>'
             f'<p>Prefer your own laptop? Clone the repo, create a Python 3.13 virtual environment and run '
             f'<code>pip install -r requirements.txt</code>.</p>'),
            ("Sign in to Azure",
             "<p>In the Codespace terminal (<b>Ctrl+`</b>):</p>" + code("az login --use-device-code") +
             "<p>Open the link, enter the code, sign in with your <b>Dialog</b> account and pick the subscription that "
             "holds the Foundry project.</p>"),
            ("Fill in .env",
             "<p>The Codespace created <code>.env</code> for you. Open it and set three values — find the first two in "
             "the Foundry portal on your project's <b>Overview</b> page and <b>Models</b> page:</p>" +
             code("FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>\n"
                  "FOUNDRY_MODEL=gpt-5.4-mini\n"
                  "PARTICIPANT_ALIAS=amila-a", ".env") +
             note("tip", "Why an alias?", "About 60 people share one project. Your alias prefixes every agent you "
                  "create (<code>amila-a-faq-agent</code>) so nobody overwrites anyone else.")),
            ("Run the check",
             code("python -m labs.lab00_check_setup") +
             "<p>You should see green ticks and a reply that starts with <i>Ayubowan</i>.</p>"),
        ],
        trouble=[
            ("az login says my sign-in was blocked",
             "Dialog's conditional access may block device-code sign-in. Run the labs in VS Code on your laptop "
             "instead (normal <code>az login</code> opens a browser), or ask Damika / Rusiru."),
            ("403 / PermissionDenied when calling the model",
             "You need the <b>Foundry User</b> role on the project. Ask the facilitators to add you."),
            ("DeploymentNotFound",
             "<code>FOUNDRY_MODEL</code> must be the <i>deployment name</i> from the Models page, not the model family name."),
        ],
    ),
    dict(
        slug="lab1", n=1, title="Your first agent", minutes=20, kind="core",
        topics=["Foundry Agent Service", "Microsoft Agent Framework", "Foundry Tools"],
        recap="<b>Microsoft Agent Framework</b> is the open-source SDK (successor to Semantic Kernel + AutoGen) for "
              "building agents in Python or .NET. Its <code>FoundryChatClient</code> runs the agent on "
              "<b>Foundry Agent Service</b> through the Responses API. An agent = <i>model + instructions + tools</i>.",
        goals=["Create an agent in code", "Give it Python function tools (customer verification, bills, outages)",
               "Add a built-in Foundry tool (code interpreter)", "Hold a multi-turn conversation with a session"],
        steps=[
            ("Read the code first",
             "<p>Open <code>labs/lab01_first_agent.py</code> and <code>labs/common/dialog_tools.py</code>. A tool is "
             "just a Python function with a docstring and typed parameters:</p>" +
             code('''@tool(approval_mode="never_require")
def check_network_outage(
    district: Annotated[str, Field(description="Sri Lankan district, e.g. Colombo, Kandy, Jaffna")],
) -> str:
    """Check for active network outages in a district."""''', "labs/common/dialog_tools.py") +
             "<p>And the agent is three lines:</p>" +
             code('''agent = Agent(
    client=client,
    name="dialog-care-copilot",
    instructions=INSTRUCTIONS,
    tools=[*ALL_TOOLS, client.get_code_interpreter_tool()],
)''', "labs/lab01_first_agent.py")),
            ("Run the scripted conversation",
             code("python -m labs.lab01_first_agent") +
             "<p>Watch it verify Nimal (mobile + NIC digits), fetch his bill, explain the VAS charge and use the code "
             "interpreter to total two months.</p>"),
            ("Chat with it yourself",
             code("python -m labs.lab01_first_agent --chat") +
             "<p>Test customers you can use:</p><div class='tablewrap'><table><tr><th>Mobile</th><th>NIC last 4</th>"
             "<th>Who</th></tr>"
             "<tr><td>0771234501</td><td>4521</td><td>Nimal · Colombo · postpaid, unpaid bill</td></tr>"
             "<tr><td>0772345602</td><td>7788</td><td>Tharushi · Kandy · prepaid, prefers Sinhala</td></tr>"
             "<tr><td>0773456703</td><td>3090</td><td>Kumaran · Jaffna · postpaid, prefers Tamil</td></tr>"
             "<tr><td>0774567804</td><td>1123</td><td>Ayesha · Galle · family plan, Singapore roaming</td></tr>"
             "<tr><td>0775678905</td><td>6402</td><td>Ruwan · Kurunegala · prepaid</td></tr></table></div>"),
            ("Break the rules on purpose",
             "<p>Ask for a bill <i>without</i> giving the NIC digits, or give the wrong ones. The tool refuses and "
             "the instructions make the agent ask again. Guardrails start with good tool design.</p>"),
        ],
        tryit="Ask in Sinhala: <code>මගේ data ඉවර වෙලා. 0772345602, NIC 7788</code>. Then add a new tool — "
              "e.g. <code>get_care_centre_hours(city)</code> — and ask about Poya-day opening hours.",
        trouble=[("The agent never calls my tool", "Check the docstring and parameter descriptions — that's all the "
                  "model sees. Make the instructions say <i>when</i> to use it.")],
    ),
    dict(
        slug="lab2", n=2, title="Ground it with Foundry IQ", minutes=20, kind="core",
        topics=["Foundry Tools", "Foundry IQ", "RAG"],
        recap="Agents must answer from <b>Dialog's documents</b>, not from memory. Two options: the built-in "
              "<b>File Search</b> tool (a vector store inside the project) or a <b>Foundry IQ knowledge base</b> — "
              "agentic retrieval on Azure AI Search that plans sub-queries, searches several sources and returns "
              "cited answers through one MCP tool, <code>knowledge_base_retrieve</code>.",
        goals=["Index the five sample policy documents", "Answer customer questions with citations",
               "See the agent refuse to invent a tariff", "Connect to a shared Foundry IQ knowledge base"],
        steps=[
            ("Look at the knowledge",
             "<p>Open <code>data/knowledge/</code>: prepaid packages, postpaid billing, roaming, troubleshooting and "
             "customer policies (all fictional, in LKR).</p>"),
            ("Part A — File Search",
             code("python -m labs.lab02_foundry_iq") +
             "<p>The script uploads the files to a vector store, attaches the <code>file_search</code> tool and asks "
             "five questions — including one in Sinhala and one whose answer is <i>not</i> in the documents.</p>"),
            ("Part B — Foundry IQ knowledge base",
             "<p>The facilitators built one shared knowledge base on Azure AI Search over the same documents. Add the "
             "values they share to <code>.env</code>, then:</p>" +
             code("FOUNDRY_IQ_MCP_URL=https://<search>.search.windows.net/knowledgebases/<kb>/mcp?api-version=...\n"
                  "FOUNDRY_IQ_CONNECTION_ID=<project connection id>", ".env") +
             code("python -m labs.lab02_foundry_iq --iq") +
             code('''knowledge_tool = client.get_mcp_tool(
    name="dialog_knowledge_base",
    url=url,
    allowed_tools=["knowledge_base_retrieve"],
    approval_mode="never_require",
    project_connection_id=os.getenv("FOUNDRY_IQ_CONNECTION_ID"),
)''', "How the agent connects")),
            ("Explore it in the portal",
             "<p>In Foundry open <b>Build → Knowledge</b> to see the knowledge base, its sources and the retrieval "
             "reasoning setting. Try a question in the knowledge base playground.</p>"),
        ],
        tryit="Change a roaming price in <code>data/knowledge/03_roaming_guide.md</code>, re-run Part A and watch the answer change.",
        trouble=[("Part B returns 401/403", "The project connection or your Search role is missing — Part A covers the same idea; carry on with it.")],
    ),
    dict(
        slug="lab3", n=3, title="Multi-agent workflow", minutes=25, kind="core",
        topics=["Multi-agent", "Orchestration", "Handoff"],
        recap="One agent with 20 tools gets confused. Split the job: a <b>triage</b> agent routes to <b>billing</b>, "
              "<b>network</b> and <b>roaming</b> specialists, each with only the tools it needs. Agent Framework ships "
              "orchestration patterns — <i>sequential, concurrent, handoff, group chat, magentic</i> — plus "
              "graph-based <b>workflows</b> with checkpoints and human-in-the-loop.",
        goals=["Build four agents with least-privilege tools", "Wire them with HandoffBuilder",
               "Watch control pass between agents in one conversation"],
        steps=[
            ("Read the orchestration",
             code('''workflow = (
    HandoffBuilder(name="dialog_care_handoff",
                   participants=[triage, billing, network, roaming],
                   termination_condition=...)
    .with_start_agent(triage)
    .build()
)''', "labs/lab03_multi_agent_handoff.py") +
             "<p>HandoffBuilder generates the <i>handoff</i> tools for you — the triage agent just decides who should take over.</p>"),
            ("Run it",
             code("python -m labs.lab03_multi_agent_handoff") +
             "<p>Tharushi reports no 4G in Peradeniya (there's an outage), then asks about Singapore roaming. Look for "
             "the <code>🔀 handoff</code> lines.</p>"),
            ("Compare the patterns",
             "<div class='tablewrap'><table><tr><th>Pattern</th><th>Use it when</th><th>Dialog example</th></tr>"
             "<tr><td>Sequential</td><td>Fixed pipeline</td><td>Summarise complaint → classify → draft reply</td></tr>"
             "<tr><td>Concurrent</td><td>Independent experts in parallel</td><td>Network, billing and fraud checks on one ticket</td></tr>"
             "<tr><td>Handoff</td><td>Conversation moves between specialists</td><td>This lab</td></tr>"
             "<tr><td>Group chat</td><td>Agents debate / review</td><td>Writer + compliance reviewer for a tariff announcement</td></tr>"
             "<tr><td>Magentic</td><td>Open-ended task, manager plans</td><td>Investigate a district-wide churn spike</td></tr>"
             "</table></div>"),
        ],
        tryit="Add a <code>fibre_agent</code> for home broadband with only <code>check_network_outage</code> and "
              "<code>raise_support_ticket</code>, and send a Tamil fibre complaint from Jaffna (there's planned maintenance in Nallur).",
        trouble=[("It loops between agents", "Tighten the triage instructions and make the termination condition explicit.")],
    ),
    dict(
        slug="lab4", n=4, title="Agent-to-Agent (A2A)", minutes=20, kind="core",
        topics=["A2A protocol", "Interoperability"],
        recap="<b>A2A</b> is an open protocol (Linux Foundation) that lets agents built by different teams, in "
              "different frameworks, discover each other through an <b>Agent Card</b> "
              "(<code>/.well-known/agent-card.json</code>) and exchange tasks over JSON-RPC. "
              "<b>MCP</b> connects an agent to <i>tools</i>; <b>A2A</b> connects an agent to <i>other agents</i>.",
        goals=["Host the Roaming agent as an A2A server", "Discover it from its Agent Card",
               "Let the Care Copilot delegate to it as a tool", "Call a neighbour's agent"],
        steps=[
            ("Start the A2A server (terminal 1)",
             code("python -m labs.lab04_a2a_server") +
             "<p>Open a second terminal (<b>+</b> in the terminal panel) and read the card:</p>" +
             code("curl -s http://localhost:9999/.well-known/agent-card.json | python -m json.tool")),
            ("Call it (terminal 2)",
             code("python -m labs.lab04_a2a_client") +
             code('''async with A2AAgent(name=card.name, agent_card=card, url=host) as roaming:
    copilot = Agent(client=..., tools=[*ALL_TOOLS,
        roaming.as_tool(name="roaming_specialist", description=card.description)])''', "The key lines")),
            ("Pair up across teams",
             "<p>In the Codespace <b>Ports</b> tab, right-click port 9999 → <b>Port visibility → Public</b> and share "
             "the URL. Your neighbour sets it and calls <i>your</i> agent:</p>" +
             code("A2A_AGENT_HOST=https://<codespace>-9999.app.github.dev python -m labs.lab04_a2a_client") +
             note("warn", "Security:", "public ports have no authentication — switch back to Private after the lab. "
                  "Production A2A endpoints sit behind Entra ID / API Management.")),
        ],
        tryit="Hosted agents in Foundry can also be called over A2A, and Foundry agents can call remote A2A agents with the built-in A2A tool — no server code.",
        trouble=[("Connection refused", "Is terminal 1 still running? A2A_AGENT_HOST must match the server URL.")],
    ),
    dict(
        slug="lab5", n=5, title="Observe and evaluate", minutes=25, kind="core",
        topics=["Observability", "Tracing", "Evaluations"],
        recap="You can't improve what you can't see. <b>Tracing</b> (OpenTelemetry → Application Insights) records "
              "every model call, tool call, token and latency. <b>Evaluations</b> score answers at scale with built-in "
              "AI judges — <i>task adherence, intent resolution, tool-call accuracy, groundedness, fluency</i> — plus "
              "your own deterministic checks.",
        goals=["Send traces to Foundry and read them", "Publish a v1 agent version to Foundry Agent Service",
               "Run a cloud evaluation over 12 test questions in 4 languages"],
        steps=[
            ("Tracing",
             code("python -m labs.lab05_observe_and_evaluate --trace") +
             code("await client.configure_azure_monitor(enable_sensitive_data=True)", "One line enables it") +
             "<p>In Foundry: <b>Build → Agents → Traces</b> (allow 2–5 minutes). Open a trace and find the "
             "<code>verify_customer</code> tool span and its token counts.</p>"),
            ("Look at the test set",
             "<p><code>data/eval/care_questions.jsonl</code> — English, Sinhala, Tamil and Singlish questions, each "
             "with the fact the answer must contain (e.g. <code>RM-ASIA-7</code>).</p>"),
            ("Run the evaluation",
             code("python -m labs.lab05_observe_and_evaluate --eval") +
             "<p>This publishes <code>&lt;alias&gt;-faq-agent</code> v1 (deliberately thin instructions) and evaluates it. "
             "Copy the printed <code>EVAL_ID=…</code> line into <code>.env</code>.</p>"),
            ("Read the results",
             "<p>The terminal shows pass rates and failing questions. In Foundry open <b>Evaluations</b> to drill into "
             "each row and the judge's reasoning.</p>"),
        ],
        trouble=[("No traces appear", "The project needs Application Insights connected (Project → Tracing). Ingestion can take 5 minutes."),
                 ("Eval run is slow", "Cloud runs queue with everyone else's — 3–8 minutes is normal. Read the traces while you wait.")],
    ),
    dict(
        slug="lab6", n=6, title="The improvement loop", minutes=20, kind="core",
        topics=["Continuous improvement", "Agent versions", "Evaluations"],
        recap="Production agents improve through a <b>signal loop</b>: <i>observe</i> (traces, user feedback) → "
              "<i>measure</i> (evals) → <i>diagnose</i> (cluster failures) → <i>fix</i> (instructions, tools, "
              "knowledge, model) → <i>re-measure</i> on the same test set → <i>ship</i> a new version with a canary. "
              "In Foundry, continuous evaluation rules score live traffic and failing traces become new test cases.",
        goals=["Diagnose the v1 failures", "Publish v2 with better instructions and grounding",
               "Re-run the same evaluation and compare runs"],
        steps=[
            ("Diagnose",
             "<p>From Lab 5: which questions failed and why? Typical: no package codes, wrong language, invented prices.</p>"),
            ("Fix",
             "<p>Edit <code>V2_INSTRUCTIONS</code> in <code>labs/lab06_improvement_loop.py</code>. It already adds the "
             "knowledge and rules — make it better.</p>"),
            ("Re-measure",
             code("python -m labs.lab06_improvement_loop") +
             "<p>In Foundry: <b>Evaluations</b> → your eval → select the v1 and v2 runs → <b>Compare</b>.</p>"),
            ("Close the loop in production (discussion)",
             "<ul><li><b>Continuous evaluation rule</b> — score a sample of live responses every hour.</li>"
             "<li><b>Agent Insights / trace clustering</b> — group failures by root cause.</li>"
             "<li><b>Agent optimization jobs</b> — try prompt/model variants against your evaluators.</li>"
             "<li><b>Versioned rollout</b> — route 10% of traffic to v2, watch the scores, then promote.</li></ul>"),
        ],
        tryit="Add three failing real-world questions to the JSONL test set — that's how a regression suite grows.",
        trouble=[],
    ),
    dict(
        slug="lab7", n=7, title="Distillation", minutes=15, kind="stretch",
        topics=["Fine-tuning", "Distillation"],
        recap="<b>Fine-tuning</b> adapts a model to your task: <i>SFT</i> (learn from examples), <i>DPO</i> (learn "
              "preferences), <i>RFT</i> (learn from a grader). <b>Distillation</b> is SFT where a large "
              "<b>teacher</b> writes the examples for a small <b>student</b> — you keep most of the quality at a "
              "fraction of the cost and latency, without the long grounding prompt.",
        goals=["Let the teacher generate questions and answers", "Write a chat-format training set",
               "(Optional) submit a fine-tuning job for the student"],
        steps=[
            ("Build the dataset (cheap)",
             code("python -m labs.lab07_distillation") +
             "<p>Open <code>data/distill/train.jsonl</code>. Each line is one conversation in the format the "
             "fine-tuning API expects.</p>"),
            ("Submit training (only if the facilitators say so)",
             code("python -m labs.lab07_distillation --submit") +
             note("warn", "Cost & time:", "training takes 30–120 minutes and is billed. Global Training processes "
                  "data outside Sri Lanka — check data-residency rules before using real customer data.")),
            ("Compare teacher vs student",
             "<p>The facilitators trained a student before the session. In Foundry open <b>Build → Fine-tuning</b> "
             "and look at the training/validation loss, then run the same Lab 5 evaluation against it.</p>"),
        ],
        tryit="Foundry can also build the training set straight from your agent's production traces (dataset generation from traces, preview).",
        trouble=[],
    ),
    dict(
        slug="lab8", n=8, title="Governance and guardrails", minutes=15, kind="stretch",
        topics=["Governance", "Guardrails", "Human-in-the-loop"],
        recap="Governance is layered: <b>identity</b> (each agent gets a Microsoft Entra Agent ID), <b>least "
              "privilege</b> (only the tools it needs), <b>human approval</b> for risky actions, <b>guardrails</b> "
              "(Prompt Shields, content filters, task adherence) on inputs, outputs and tool calls, and the "
              "<b>Foundry Control Plane</b> to inventory, monitor and stop agents across the organisation.",
        goals=["Require a supervisor's approval before money is credited", "Attack your agent and see what's blocked",
               "Find your agent in the Control Plane"],
        steps=[
            ("Human approval",
             code('''apply_bill_credit = tool(_credit_tool.func, name="apply_bill_credit",
                         description=_credit_tool.description,
                         approval_mode="always_require")''', "labs/lab08_governance.py") +
             code("python -m labs.lab08_governance") +
             "<p>Answer <b>y</b> or <b>n</b> when the agent asks to credit the account.</p>"),
            ("Attacks",
             "<p>The same script sends a jailbreak, a social-engineering prompt and an indirect injection hidden in a "
             "customer email. Note which are stopped by the <b>guardrail</b> (an API error) and which by the "
             "<b>instructions</b>.</p>"),
            ("Explore the portal",
             "<ul><li><b>Operate → Assets</b>: every agent in the project, its versions and owners.</li>"
             "<li>Your agent → <b>Guardrails</b>: the policy applied to it.</li>"
             "<li>Your agent → <b>Identity</b>: its Entra Agent ID.</li></ul>"),
        ],
        trouble=[],
    ),
]


def lab_page(i: int, lab: dict) -> str:
    goals = "".join(f"<li>{g}</li>" for g in lab["goals"])
    steps = "".join(f"<li><h3>{t}</h3>{h}</li>" for t, h in lab["steps"])
    body = (f'<div class="recap"><b>Theory recap ·</b> {lab["recap"]}</div>'
            f'<div class="goal"><b>In this lab you will</b><ul>{goals}</ul></div>'
            f'<h2 class="sec">Steps</h2><ol class="steps">{steps}</ol>')
    if lab.get("tryit"):
        body += note("try", "🧪 Try it:", lab["tryit"])
    if lab["trouble"]:
        body += '<h2 class="sec">Troubleshooting</h2>' + "".join(
            f'<details class="trouble"><summary>{q}</summary><p>{a}</p></details>' for q, a in lab["trouble"])
    body += (f'<p style="margin-top:18px">Stuck or behind? The complete code for every lab is already in '
             f'<code>labs/</code> — run it, read it, move on.</p>')
    prev = LABS[i - 1] if i > 0 else None
    nxt = LABS[i + 1] if i + 1 < len(LABS) else None
    nav = '<div class="stepnav">'
    nav += (f'<a href="{prev["slug"]}.html">← Lab {prev["n"]}<span>{prev["title"]}</span></a>' if prev
            else '<a href="prerequisites.html">← Prerequisites<span>Before the day</span></a>')
    nav += (f'<a class="next" href="{nxt["slug"]}.html">Lab {nxt["n"]} →<span>{nxt["title"]}</span></a>' if nxt
            else '<a class="next" href="../home.html">Finish →<span>Back to the workshop home</span></a>')
    body += nav + "</div>"
    chips = [f"⏱ {lab['minutes']} min", "Core" if lab["kind"] == "core" else "Stretch", *lab["topics"]]
    return page(f"Lab {lab['n']} · {lab['title']}", f"Lab {lab['n']} · {lab['title']}",
                "Dialog Care Copilot — build it step by step.", body, chips=chips)


# --------------------------------------------------------------------------- home
AGENDA = [
    ("09:00", "04:30", "Welcome, scenario, open your Codespace (Lab 0)", "Suranga"),
    ("09:10", "04:40", "Theory · Agent Service, Agent Framework, A2A, Foundry Tools & IQ", "Suranga"),
    ("10:00", "05:30", "Theory · Multi-agent orchestration, evaluations, improvement loop, fine-tuning & distillation, governance", "Suranga"),
    ("11:00", "06:30", "Break", ""),
    ("11:15", "06:45", "Hands-on · Labs 1–6 (core) and 7–8 (stretch)", "Damika & Rusiru"),
    ("13:15", "08:45", "Show & tell · 2–3 teams demo their Copilot · wrap-up", "All"),
]

ARCH_SVG = """<svg viewBox="0 0 900 330" role="img" aria-label="Dialog Care Copilot architecture" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif" font-size="13">
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
<g fill="none" stroke="currentColor" stroke-width="1.4" style="color:var(--muted)">
<path d="M120 165 H178" marker-end="url(#a)"/><path d="M300 165 C340 165 340 70 378 70" marker-end="url(#a)"/>
<path d="M300 165 H378" marker-end="url(#a)"/><path d="M300 165 C340 165 340 260 378 260" marker-end="url(#a)"/>
<path d="M520 70 H598" marker-end="url(#a)"/><path d="M520 165 H598" marker-end="url(#a)"/><path d="M520 260 H598" marker-end="url(#a)"/>
</g>
<g><rect x="20" y="140" width="100" height="50" rx="10" fill="var(--panel)" stroke="var(--border)"/><text x="70" y="162" text-anchor="middle" fill="var(--ink)">Customer</text><text x="70" y="178" text-anchor="middle" fill="var(--muted)" font-size="11">EN · සිං · தமிழ்</text></g>
<g><rect x="180" y="135" width="120" height="60" rx="10" fill="var(--dialog)"/><text x="240" y="161" text-anchor="middle" fill="#fff" font-weight="600">Triage agent</text><text x="240" y="178" text-anchor="middle" fill="#fff" font-size="11">Lab 1 · Lab 3</text></g>
<g fill="var(--foundry)"><rect x="380" y="45" width="140" height="50" rx="10"/><rect x="380" y="140" width="140" height="50" rx="10"/><rect x="380" y="235" width="140" height="50" rx="10"/></g>
<g fill="#fff" text-anchor="middle" font-weight="600"><text x="450" y="75">Billing agent</text><text x="450" y="170">Network agent</text><text x="450" y="258">Roaming agent</text></g>
<text x="450" y="275" text-anchor="middle" fill="#fff" font-size="11">served over A2A · Lab 4</text>
<g fill="var(--card)" stroke="var(--border)"><rect x="600" y="45" width="280" height="50" rx="10"/><rect x="600" y="140" width="280" height="50" rx="10"/><rect x="600" y="235" width="280" height="50" rx="10"/></g>
<g fill="var(--ink)"><text x="614" y="66">Tools: verify · bill · credit (approval)</text><text x="614" y="84" fill="var(--muted)" font-size="11">Function tools · Lab 1 · Lab 8</text>
<text x="614" y="161">Tools: outage check · tickets</text><text x="614" y="179" fill="var(--muted)" font-size="11">Least-privilege tools · Lab 3</text>
<text x="614" y="256">Knowledge: Foundry IQ knowledge base</text><text x="614" y="274" fill="var(--muted)" font-size="11">Agentic retrieval over policy docs · Lab 2</text></g>
<rect x="20" y="300" width="860" height="26" rx="8" fill="var(--foundry-soft)"/>
<text x="450" y="318" text-anchor="middle" fill="var(--ink)" font-size="12">Across everything: traces → evaluations → improvement loop (Labs 5–6) · distillation (Lab 7) · guardrails & Control Plane (Lab 8)</text>
</svg>"""


def home() -> str:
    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in AGENDA)
    cards = "".join(
        f'<a class="card {lab["kind"]}" href="pages/{lab["slug"]}.html"><span class="t">⏱ {lab["minutes"]} min</span>'
        f'<div class="k">Lab {lab["n"]} · {"core" if lab["kind"] == "core" else "stretch"}</div>'
        f'<h3>{lab["title"]}</h3><p>{" · ".join(lab["topics"])}</p></a>' for lab in LABS)
    body = f"""
<div class="ctas"><a class="cta" href="{CODESPACE}">Open in Codespaces ↗</a>
<a class="cta alt" href="pages/prerequisites.html">Prerequisites</a>
<a class="cta alt" href="pages/concepts.html">Concept guide</a></div>

<h2 class="sec">The scenario — Dialog Care Copilot</h2>
<p>You build a customer-care agent for a Sri Lankan telco that answers in English, Sinhala and Tamil, checks
outages by district, explains bills in LKR, recommends roaming passes for Singapore, India, the Maldives and the
Gulf — and gets measurably better through evaluation.</p>
<figure class="diagram">{ARCH_SVG}<figcaption>What you will have built by the end of the labs.</figcaption></figure>

<h2 class="sec">Hands-on labs</h2>
<div class="cards">{cards}</div>
{note("tip", "Pace:", "Labs 0–6 are the core path (≈2 hours). Fast? Continue with 7–8. Behind? The finished code is in <code>labs/</code> — run it and keep going.")}

<h2 class="sec">Agenda</h2>
<div class="tablewrap"><table class="agenda"><tr><th>Sri Lanka</th><th>Sweden</th><th>Session</th><th>Lead</th></tr>{rows}</table></div>

<h2 class="sec">People</h2>
<div class="cards">
<div class="card"><div class="k">Theory</div><h3>Suranga Nanayakkara</h3><p>Consultant – Data &amp; AI · Microsoft Certified Trainer</p></div>
<div class="card"><div class="k">Hands-on</div><h3>Damika Saputhanthri</h3><p>Data &amp; AI Engineer, ICT &amp; Digital Solutions</p></div>
<div class="card"><div class="k">Hands-on</div><h3>Rusiru Chathushanka</h3><p>Associate Tech Lead</p></div>
</div>

<h2 class="sec">Contributing</h2>
<p>Found a fix or improvement during the labs? Open a pull request on <a href="{REPO}">the repository</a>.</p>
"""
    return page("Dialog × Microsoft Foundry Agents Workshop", "Build, evaluate and govern AI agents with Microsoft Foundry",
                DATE + " · Microsoft office Colombo + online", body, depth=0,
                chips=["Microsoft Agent Framework", "Foundry Agent Service", "A2A", "Foundry IQ", "Evaluations",
                       "Distillation", "Governance"])


def landing() -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Foundry Agents Workshop</title><link rel="stylesheet" href="assets/site.css"></head>
<body><section class="hero">{BRAND}
<h1>From one agent to a <span class="accent">governed multi-agent system</span></h1>
<p class="sub">A hands-on Microsoft Foundry workshop for the Dialog team: Agent Framework, A2A, Foundry IQ,
evaluations, distillation and governance — built around a Sri Lankan customer-care copilot.</p>
<a class="cta" href="home.html">Start the workshop →</a>
<div class="meta">{DATE}</div></section>
<script src="assets/site.js"></script></body></html>"""


CONCEPTS = [
    ("Microsoft Foundry", "Microsoft's platform for building, running and governing AI apps and agents: model "
     "catalogue, Agent Service, Foundry IQ, Tools, evaluations, observability and the Control Plane, organised in "
     "<i>resources</i> and <i>projects</i>."),
    ("Foundry Agent Service", "The managed runtime for agents. <b>Prompt agents</b> are defined declaratively "
     "(model + instructions + tools) and versioned; <b>hosted agents</b> run your own container code. Both are "
     "called through the OpenAI-compatible Responses API."),
    ("Microsoft Agent Framework", "Open-source SDK for Python and .NET that unifies Semantic Kernel and AutoGen: "
     "agents, tools, sessions, middleware, multi-agent orchestrations and graph-based workflows. GA since April 2026."),
    ("A2A (Agent-to-Agent)", "Open protocol for agents to discover each other (Agent Card) and exchange tasks, "
     "messages and artifacts across frameworks and vendors. Complements MCP, which connects agents to tools."),
    ("Foundry Tools", "Built-in and connected tools an agent can call: code interpreter, file search, web search, "
     "MCP servers, OpenAPI, Azure Functions, A2A and more. Toolboxes bundle tools behind one MCP endpoint."),
    ("Foundry IQ", "Knowledge bases built on Azure AI Search agentic retrieval. The agent asks one question; the "
     "knowledge base plans sub-queries across sources and returns grounded, cited results."),
    ("Orchestration patterns", "Sequential, concurrent, handoff, group chat and magentic; or explicit workflows of "
     "executors and edges with checkpointing and human-in-the-loop."),
    ("Evaluations", "Measure quality and safety at scale: agent evaluators (intent resolution, task adherence, tool "
     "call accuracy), RAG evaluators (groundedness, relevance), safety evaluators, custom graders and red teaming. "
     "Run locally, in the cloud, on a schedule or continuously on live traffic."),
    ("Continuous improvement loop", "Observe → measure → diagnose → fix → re-measure → ship. Traces and user "
     "feedback become test cases; every change ships as a new agent version, evaluated before full rollout."),
    ("Fine-tuning", "SFT (examples), DPO (preferred vs rejected answers) and RFT (reward from a grader). Global "
     "Training and the Developer tier lower the cost of experiments."),
    ("Distillation", "A large teacher model generates high-quality outputs that become the training data for a "
     "smaller, cheaper student model — keeping quality while cutting cost and latency."),
    ("Observability", "OpenTelemetry tracing of every model call, tool call and handoff into Application Insights, "
     "with dashboards for latency, tokens, cost and evaluation scores."),
    ("Governance", "Entra Agent ID for every agent, RBAC (Foundry User / Project Manager / Account Owner), "
     "guardrails (Prompt Shields, content filters, task adherence), the AI Gateway in API Management, and the "
     "Foundry Control Plane for fleet-wide inventory, policy and cost."),
    ("Region & data residency", "This workshop uses <b>Southeast Asia</b>. Global Standard deployments may process "
     "prompts in any region while data at rest stays in the resource's geography; check Global Training and "
     "Developer-tier fine-tuning against Dialog's data-handling policy before using real customer data."),
]


def concepts() -> str:
    body = "".join(f'<div class="card" style="margin-bottom:12px"><h3>{t}</h3><p>{d}</p></div>' for t, d in CONCEPTS)
    return page("Concept guide", "Concept guide", "The ideas behind the labs, in plain language.", body)


def prereqs() -> str:
    body = f"""
<ol class="steps">
<li><h3>Access to a Microsoft Foundry project with a model</h3>
<p>Either access to a Foundry project that already has a chat model deployed (recommended <code>gpt-5.4-mini</code>),
or permission to deploy one yourself. The workshop uses the <b>Southeast Asia</b> region.</p>
<p>Check: open <a href="https://ai.azure.com">ai.azure.com</a> → your project → copy the <b>project endpoint</b> from
Overview and the <b>deployment name</b> from Models → say “Ayubowan!” in the Playground. You need at least the
<b>Foundry User</b> role.</p></li>
<li><h3>A GitHub account</h3><p>Personal accounts are fine. Codespaces includes free monthly hours — the workshop uses about 10.</p></li>
<li><h3>A laptop with Chrome or Edge</h3><p>Nothing to install. Optional local alternative: VS Code, Python 3.13, Git, Azure CLI.</p></li>
<li><h3>Test sign-in from a Codespace (5 minutes — important)</h3>
<div class="ctas"><a class="cta" href="{CODESPACE}">Open in Codespaces ↗</a></div>
{code("az login --use-device-code")}
<p>If your Dialog sign-in is blocked, reply to the invitation before Monday so we can arrange a fallback.</p></li>
</ol>
<h2 class="sec">Nice to have — enables the advanced labs</h2>
<div class="tablewrap"><table><tr><th>Feature</th><th>Lab</th><th>Needed in the project</th></tr>
<tr><td>Application Insights connected</td><td>5 · tracing</td><td>Project → Tracing → connect</td></tr>
<tr><td>Azure AI Search connected</td><td>2 · Foundry IQ</td><td>Search service (Basic+) connected to the project</td></tr>
<tr><td>Fine-tuning permission</td><td>7 · distillation</td><td><code>gpt-4.1-mini</code> with Global Training</td></tr></table></div>
<div class="stepnav"><a href="../home.html">← Workshop home<span>Agenda and labs</span></a>
<a class="next" href="lab0.html">Lab 0 →<span>Set up your environment</span></a></div>"""
    return page("Prerequisites", "Prerequisites", "Please complete these before Monday morning.", body)


def main() -> None:
    (OUT / "pages").mkdir(exist_ok=True)
    (OUT / "index.html").write_text(landing())
    (OUT / "home.html").write_text(home())
    (OUT / "pages" / "concepts.html").write_text(concepts())
    (OUT / "pages" / "prerequisites.html").write_text(prereqs())
    for i, lab in enumerate(LABS):
        (OUT / "pages" / f"{lab['slug']}.html").write_text(lab_page(i, lab))
    (OUT / ".nojekyll").write_text("")
    print(f"Built {len(LABS) + 4} pages into {OUT}")


if __name__ == "__main__":
    main()
