# Dialog × Microsoft Foundry — Agents Workshop

Hands-on workshop for the Dialog Axiata engineering team, delivered by **hONE**.
Monday 26 October 2026 · 09:00–13:30 Sri Lanka time.

You build **Dialog Care Copilot**, a customer-care agent for a Sri Lankan telco, and grow it lab by lab:

| Lab | Topic | Script |
|---|---|---|
| 0 | Setup check | `python -m labs.lab00_check_setup` |
| 1 | Foundry Agent Service + Microsoft Agent Framework + Foundry Tools | `python -m labs.lab01_first_agent` |
| 2 | Foundry IQ — grounding on documents | `python -m labs.lab02_foundry_iq` |
| 3 | Multi-agent workflow — handoff orchestration | `python -m labs.lab03_multi_agent_handoff` |
| 4 | A2A — agent-to-agent protocol | `python -m labs.lab04_a2a_server` + `python -m labs.lab04_a2a_client` |
| 5 | Observability + evaluations | `python -m labs.lab05_observe_and_evaluate --trace` / `--eval` |
| 6 | Continuous-improvement loop | `python -m labs.lab06_improvement_loop` |
| 7 | Distillation (stretch) | `python -m labs.lab07_distillation` |
| 8 | Governance & guardrails (stretch) | `python -m labs.lab08_governance` |

**Start here:** [PREREQUISITES.md](PREREQUISITES.md) → open in Codespaces → install dependencies with `python -m pip install -r requirements.txt` → sign in with `az login --use-device-code` → run Lab 0 with `python -m labs.lab00_check_setup`.

> All customers, packages and prices in `data/` are **fictional sample data** for training — not real Dialog tariffs.

Built on Microsoft Agent Framework 1.23 and azure-ai-projects 2.7 (versions pinned in `requirements.txt`).
