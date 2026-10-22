"""Lab 7 — Distillation: teach a small, cheap model to behave like a big one.

    teacher (large model + long grounded prompt)  →  answers  →  JSONL training set
    →  supervised fine-tuning of a small student model  →  evaluate student vs teacher

Why: the v2 FAQ agent from Lab 6 sends ~4,000 tokens of knowledge with EVERY request.
A distilled student learns the style and facts, so each call needs a short prompt
and a cheaper model → lower cost and latency at Dialog's call-centre volumes.

Steps in this script:
  1. Generate customer questions (the teacher writes realistic variations)
  2. The teacher answers each one using the full grounded prompt
  3. Write data/distill/train.jsonl + valid.jsonl in chat fine-tuning format
  4. (--submit) upload the files and start a fine-tuning job on the student model

Fine-tuning takes 30–120 minutes, so in the workshop we only submit and then look at
the facilitators' pre-trained student in Foundry (Build → Fine-tuning).

Run:  python -m labs.lab07_distillation            (build the dataset only — cheap)
      python -m labs.lab07_distillation --submit   (also start the training job — costs money!)
"""

import json
import os
import random
import sys

from labs.common.config import DATA_DIR, alias, require
from labs.common.foundry_eval import project_client
from labs.lab06_improvement_loop import V2_INSTRUCTIONS

STUDENT_SYSTEM = "You are Dialog Care Copilot for a Sri Lankan mobile operator. Quote package codes and LKR prices."
TOPICS = ["roaming passes for a specific country and trip length", "postpaid bill due dates and late fees",
          "prepaid data packages", "SIM replacement and eSIM", "billing disputes and refunds",
          "mobile data troubleshooting", "fibre broadband faults"]


def teacher_answer(oai, model: str, question: str) -> str:
    return oai.responses.create(model=model, instructions=V2_INSTRUCTIONS, input=question).output_text


def generate_questions(oai, model: str, per_topic: int) -> list[str]:
    questions: list[str] = []
    for topic in TOPICS:
        prompt = (f"Write {per_topic} different, realistic customer questions about {topic} for a Sri Lankan "
                  "mobile operator. Mix English, Sinhala, Tamil and Singlish. Return a JSON array of strings only.")
        text = oai.responses.create(model=model, input=prompt).output_text
        questions += json.loads(text[text.find("["): text.rfind("]") + 1])
    return questions


def main() -> None:
    teacher = os.getenv("TEACHER_MODEL") or require("FOUNDRY_MODEL")
    student_base = os.getenv("STUDENT_BASE_MODEL", "gpt-4.1-mini")
    out_dir = DATA_DIR / "distill"
    out_dir.mkdir(exist_ok=True)

    with project_client() as project, project.get_openai_client() as oai:
        print(f"1️⃣  Teacher {teacher} is writing questions…")
        questions = generate_questions(oai, teacher, per_topic=6)
        print(f"2️⃣  Teacher is answering {len(questions)} questions…")
        rows = []
        for i, q in enumerate(questions, 1):
            rows.append({"messages": [
                {"role": "system", "content": STUDENT_SYSTEM},
                {"role": "user", "content": q},
                {"role": "assistant", "content": teacher_answer(oai, teacher, q)},
            ]})
            print(f"   {i}/{len(questions)}", end="\r")

        random.seed(7)
        random.shuffle(rows)
        cut = max(10, int(len(rows) * 0.8))
        for name, part in (("train", rows[:cut]), ("valid", rows[cut:])):
            (out_dir / f"{name}.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in part) + "\n")
        print(f"\n3️⃣  Wrote {cut} training and {len(rows) - cut} validation examples to data/distill/")

        if "--submit" not in sys.argv:
            print("   Open data/distill/train.jsonl and read a few examples. Run with --submit to train.")
            return

        print(f"4️⃣  Uploading and starting fine-tuning of {student_base}…")
        files = {}
        for name in ("train", "valid"):
            with open(out_dir / f"{name}.jsonl", "rb") as f:
                files[name] = oai.files.create(file=f, purpose="fine-tune")
            oai.files.wait_for_processing(files[name].id)
        job = oai.fine_tuning.jobs.create(
            training_file=files["train"].id,
            validation_file=files["valid"].id,
            model=student_base,
            suffix=f"dialog-{alias()}"[:18],
            method={"type": "supervised", "supervised": {"hyperparameters": {"n_epochs": 3}}},
            # GlobalStandard = Global Training (works from Asian regions; data may be processed outside Sri Lanka)
            extra_body={"trainingType": os.getenv("FT_TRAINING_TYPE", "GlobalStandard")},
        )
        print(f"   ✅ Job {job.id} — status {job.status}. Watch it in Foundry → Build → Fine-tuning.")


if __name__ == "__main__":
    main()
