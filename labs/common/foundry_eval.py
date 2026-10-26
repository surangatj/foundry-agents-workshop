"""Helpers for Labs 5–6: publish versioned prompt agents and run cloud evaluations in Foundry.

Uses the azure-ai-projects 2.x SDK (agents.create_version + OpenAI-compatible evals API).
"""

import json
import time

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAIAgentTargetParam,
    PromptAgentDefinition,
    TargetCompletionEvalRunDataSource,
    TestingCriterionAzureAIEvaluator,
)
from .config import DATA_DIR, KNOWLEDGE_DIR, agent_name, project_client, require

FAQ_AGENT = "faq-agent"


def knowledge_text() -> str:
    return "\n\n".join(p.read_text(encoding="utf-8") for p in sorted(KNOWLEDGE_DIR.glob("*.md")))


def publish_agent(project: AIProjectClient, instructions: str):
    """Create a new VERSION of your FAQ agent in Foundry (visible under Build → Agents)."""
    return project.agents.create_version(
        agent_name=agent_name(FAQ_AGENT),
        definition=PromptAgentDefinition(model=require("FOUNDRY_MODEL"), instructions=instructions),
    )


def create_eval(openai_client, name: str):
    model = require("FOUNDRY_MODEL")
    judge = {"model": model}
    criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator", name="task_adherence", evaluator_name="builtin.task_adherence",
            initialization_parameters=judge,
            data_mapping={"query": "{{item.query}}", "response": "{{sample.output_items}}"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator", name="intent_resolution", evaluator_name="builtin.intent_resolution",
            initialization_parameters=judge,
            data_mapping={"query": "{{item.query}}", "response": "{{sample.output_items}}"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator", name="fluency", evaluator_name="builtin.fluency",
            initialization_parameters=judge,
            data_mapping={"query": "{{item.query}}", "response": "{{sample.output_text}}"},
        ),
        # Deterministic check: does the answer contain the expected package code / fact?
        {"type": "string_check", "name": "has_expected_fact", "input": "{{sample.output_text}}",
         "reference": "{{item.expected}}", "operation": "ilike"},
    ]
    return openai_client.evals.create(
        name=name,
        data_source_config={
            "type": "custom",
            "item_schema": {"type": "object",
                            "properties": {"query": {"type": "string"}, "expected": {"type": "string"}},
                            "required": ["query", "expected"]},
            "include_sample_schema": True,
        },
        testing_criteria=criteria,
    )


def run_eval(openai_client, eval_id: str, agent, label: str, *, timeout_seconds: float = 1200):
    if timeout_seconds <= 0:
        raise ValueError("Evaluation timeout must be positive.")
    rows = [json.loads(line) for line in (DATA_DIR / "eval" / "care_questions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError("The evaluation dataset is empty.")
    data_source = TargetCompletionEvalRunDataSource(
        type="azure_ai_target_completions",
        source={"type": "file_content", "content": [{"item": row} for row in rows]},
        input_messages={"type": "template", "template": [
            {"type": "message", "role": "user", "content": {"type": "input_text", "text": "{{item.query}}"}}]},
        target=AzureAIAgentTargetParam(type="azure_ai_agent", name=agent.name, version=agent.version),
    )
    run = openai_client.evals.runs.create(eval_id=eval_id, name=label, data_source=data_source)
    print(f"   ⏳ evaluation run '{label}' started — {len(rows)} test questions")
    deadline = time.monotonic() + timeout_seconds
    while run.status not in ("completed", "failed", "canceled", "cancelled"):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(
                f"Evaluation {run.id} exceeded {timeout_seconds:g} seconds. "
                "The cloud run may still be active; inspect or cancel it in Foundry."
            )
        time.sleep(min(10, remaining))
        run = openai_client.evals.runs.retrieve(run_id=run.id, eval_id=eval_id)
        print(f"      status: {run.status}")
    if run.status != "completed":
        raise RuntimeError(f"Evaluation {run.id} {run.status}: {getattr(run, 'error', None) or 'see Foundry for details'}")
    return run


def summarise(openai_client, eval_id: str, run) -> dict[str, float]:
    """Pass-rate per evaluator, plus the failing questions."""
    if run.status != "completed":
        raise RuntimeError(f"Cannot summarise evaluation {run.id}: status is {run.status}.")
    passed: dict[str, list[bool]] = {}
    failures: list[str] = []
    for item in openai_client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_id):
        for result in item.results or []:
            r = result if isinstance(result, dict) else result.model_dump()
            passed.setdefault(r.get("name", "?"), []).append(bool(r.get("passed")))
            if not r.get("passed"):
                query = (item.datasource_item or {}).get("query", "")
                failures.append(f"✗ {r.get('name')}: {query[:80]}")
    rates = {name: sum(v) / len(v) for name, v in passed.items() if v}
    if not rates:
        raise RuntimeError(f"Evaluation {run.id} completed without evaluator results; inspect the run in Foundry.")
    for name, rate in rates.items():
        print(f"   {name:<22} {rate:6.0%}  {'█' * round(rate * 20)}")
    if failures:
        print("\n   Failing cases:\n   " + "\n   ".join(sorted(set(failures))[:15]))
    return rates
