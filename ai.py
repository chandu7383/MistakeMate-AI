import json
from openai import OpenAI

MODEL = "gpt-5.6-luna"

SYSTEM_PROMPT = """
You are MistakeMate AI, a patient AI teacher.

Your job is to evaluate a student's answer against a question and teach the
student from mistakes.

Important:
- Do NOT invent a mistake just to find something.
- Distinguish between Concept, Grammar, Missing Point, Calculation, and Fact mistakes.
- If the answer is correct, say so.
- Be concise but educational.
- Explain the mistake in simple language.
- Give a corrected version.
- Give a simple real-life example when useful.
- Give a memory tip.
- Suggest weak topics only when supported by the answer.
- Return ONLY valid JSON.
"""

SCHEMA = {
    "overall_status": "Correct | Partially Correct | Incorrect",
    "score": 0,
    "mistakes": [
        {
            "type": "Concept | Grammar | Missing Point | Calculation | Fact",
            "wrong_part": "string",
            "why_wrong": "string",
            "correct_version": "string"
        }
    ],
    "simple_explanation": "string",
    "easy_example": "string",
    "remember_tip": "string",
    "practice_question": "string",
    "weak_topics": ["string"]
}

def analyze_answer(question: str, answer: str) -> dict:
    client = OpenAI()

    user_prompt = f"""
QUESTION:
{question}

STUDENT ANSWER:
{answer}

Return JSON matching this structure:
{json.dumps(SCHEMA, ensure_ascii=False, indent=2)}
"""

    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=user_prompt
    )

    text = response.output_text.strip()

    # Remove accidental markdown fences if the model adds them.
    if text.startswith("```"):
        text = text.replace("```json", "", 1).replace("```", "", 1).strip()

    result = json.loads(text)

    result["score"] = max(0, min(100, int(result.get("score", 0))))
    result.setdefault("mistakes", [])
    result.setdefault("weak_topics", [])
    return result