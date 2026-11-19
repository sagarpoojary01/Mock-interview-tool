"""LLM layer. Uses Groq (Llama 3.1 8B) when GROQ_API_KEY is set, otherwise a mock."""
import json
import re

from app import config

QUESTION_PROMPT = (
    "You are a technical interviewer. Generate exactly {n} interview questions for a "
    "{level} {role}. Return ONLY a JSON array of strings."
)
EVAL_PROMPT = (
    "You are a strict but fair interviewer for a {level} {role} role. Score the "
    "candidate's answer from 1 to 10 and give 2-3 sentences of actionable feedback. "
    'Return ONLY JSON like {{"score": 7, "feedback": "..."}}.'
)


def _client():
    from groq import Groq

    return Groq(api_key=config.GROQ_API_KEY)


def _chat(system: str, user: str) -> str:
    resp = _client().chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.4,
    )
    return resp.choices[0].message.content


def _extract_json(text: str):
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    return json.loads(match.group(1) if match else text)


def generate_questions(role: str, level: str, n: int) -> list[str]:
    if not config.GROQ_API_KEY:
        base = [
            f"Tell me about a project that made you a strong fit for a {level} {role} role.",
            f"What are the core concepts every {role} must know well?",
            "Describe a bug that was hard to find and how you fixed it.",
            "How do you structure and test your code so it stays maintainable?",
            "Where do you see gaps in your skills and how are you closing them?",
            "Explain a trade-off you made between speed and quality.",
            "How do you handle disagreements in code review?",
            "Walk me through how you would design a simple REST API.",
            "How do you debug a slow database query?",
            "Describe how you keep secrets and credentials safe.",
        ]
        return base[:n]
    raw = _chat(QUESTION_PROMPT.format(n=n, level=level, role=role), "Generate the questions.")
    questions = [str(q).strip() for q in _extract_json(raw) if str(q).strip()]
    return questions[:n]


def evaluate_answer(role: str, level: str, question: str, answer: str) -> tuple[int, str]:
    if not config.GROQ_API_KEY:
        words = len(answer.split())
        score = max(1, min(10, 2 + words // 12))
        feedback = (
            "Mock evaluation (no GROQ_API_KEY set). "
            + ("Good depth - add a concrete example." if score >= 6 else "Too brief - expand with specifics, examples and trade-offs.")
        )
        return score, feedback
    raw = _chat(
        EVAL_PROMPT.format(level=level, role=role),
        f"Question: {question}\n\nCandidate answer: {answer}",
    )
    data = _extract_json(raw)
    score = max(1, min(10, int(data["score"])))
    return score, str(data["feedback"]).strip()
