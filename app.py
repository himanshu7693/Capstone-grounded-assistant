"""
Task 4: Guardrailed Assistant

A small assistant that:
- stays within a defined remit (Python + Generative AI fundamentals),
- blocks a simple set of unsafe/off-topic requests before calling the model,
- records token usage when the API reports it,
- estimates API cost from measured token usage.

Set GEMINI_API_KEY before running.
"""

import os
import re
from dataclasses import dataclass
from typing import Literal

from google import genai


ALLOWED_TOPICS = [
    "python programming",
    "generative ai",
    "large language models",
    "prompt engineering",
    "machine learning fundamentals",
    "software development",
]

# These are deliberately simple, transparent guardrails for a small project.
UNSAFE_PATTERNS = [
    r"\bhow to (make|build|create)\b.*\b(bomb|explosive)\b",
    r"\bhow to\b.*\b(steal|hack)\b.*\bpassword\b",
    r"\bmake\b.*\bweapon\b",
    r"\bhow to\b.*\bkill\b",
]

OFF_TOPIC_PATTERNS = [
    r"\bweather\b",
    r"\bfootball score\b",
    r"\bcelebrity gossip\b",
    r"\brecipe for\b",
    r"\bstock price\b",
]


@dataclass
class Result:
    decision: Literal["allowed", "off_topic", "unsafe"]
    answer: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float


def classify_request(text: str) -> Literal["allowed", "off_topic", "unsafe"]:
    """Apply deterministic guardrails before an LLM call."""
    lowered = text.lower()

    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, lowered):
            return "unsafe"

    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, lowered):
            return "off_topic"

    # Explicit topic keywords provide a lightweight remit check.
    topic_words = [
        "python", "llm", "generative ai", "prompt", "machine learning",
        "embedding", "transformer", "rag", "token", "model", "api",
        "neural network", "fine-tuning", "fine tuning", "code", "programming",
    ]

    if any(word in lowered for word in topic_words):
        return "allowed"

    return "off_topic"


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Example cost estimate.

    Gemini free-tier usage can be $0 within applicable quota.
    The formula below is intentionally configurable and demonstrates
    how measured token usage can be converted into a cost estimate.
    Set GEMINI_INPUT_PRICE_PER_MILLION and GEMINI_OUTPUT_PRICE_PER_MILLION
    if a paid model/pricing plan is being used.
    """
    input_price = float(os.getenv("GEMINI_INPUT_PRICE_PER_MILLION", "0"))
    output_price = float(os.getenv("GEMINI_OUTPUT_PRICE_PER_MILLION", "0"))

    return (
        (input_tokens / 1_000_000) * input_price
        + (output_tokens / 1_000_000) * output_price
    )


def ask_assistant(user_text: str) -> Result:
    decision = classify_request(user_text)

    if decision == "unsafe":
        return Result(
            decision="unsafe",
            answer="I can't help with that request.",
            input_tokens=0,
            output_tokens=0,
            estimated_cost_usd=0.0,
        )

    if decision == "off_topic":
        return Result(
            decision="off_topic",
            answer=(
                "I can only help with Python, Generative AI, LLMs, "
                "prompt engineering, and related technical fundamentals."
            ),
            input_tokens=0,
            output_tokens=0,
            estimated_cost_usd=0.0,
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add your Gemini API key as an environment variable."
        )

    client = genai.Client(api_key=api_key)

    system_instruction = """
You are a narrowly scoped technical study assistant.

Your remit:
- Python programming
- Generative AI and LLM fundamentals
- Prompt engineering
- Machine learning fundamentals
- RAG, embeddings, APIs, and related software-development concepts

Stay inside this remit.
If the user asks an unrelated question, politely refuse and say what topics you support.
Do not provide instructions that facilitate violence, weapon construction, credential theft,
malware, or other harmful wrongdoing.
For allowed questions, give a concise educational answer.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_text,
        config={"system_instruction": system_instruction},
    )

    usage = getattr(response, "usage_metadata", None)
    input_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
    output_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)

    return Result(
        decision="allowed",
        answer=response.text.strip(),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimate_cost(input_tokens, output_tokens),
    )


if __name__ == "__main__":
    question = input("Ask the assistant: ").strip()
    result = ask_assistant(question)

    print("\nDecision:", result.decision)
    print("Answer:", result.answer)
    print("Input tokens:", result.input_tokens)
    print("Output tokens:", result.output_tokens)
    print(f"Estimated cost: ${result.estimated_cost_usd:.6f}")
