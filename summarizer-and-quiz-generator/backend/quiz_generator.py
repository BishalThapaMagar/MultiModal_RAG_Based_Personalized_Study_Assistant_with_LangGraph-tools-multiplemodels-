import json
import re
import sys
from pathlib import Path

# Add ai_services to path
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from ai_services.GroqClient import generate_completion

def call_llama(prompt: str) -> str:
    """Use GroqClient instead of local Ollama."""
    return generate_completion(prompt)

def generate_quiz(summary: str, num_questions=5):
    """Generate MCQ quiz as JSON objects."""
    prompt = f"""
    Based on this summary, create {num_questions} multiple-choice questions.
    Each question should have 4 options and exactly 1 correct answer.
    Return ONLY valid JSON array, no explanations.

    Example format:
    [
      {{
        "question": "What is the capital of France?",
        "options": ["Paris", "Berlin", "London", "Madrid"],
        "answer": "Paris"
      }}
    ]

    Summary:
    {summary}
    """

    raw_output = call_llama(prompt)

    # ---- Try to extract JSON safely ----
    try:
        # Sometimes model adds text → extract JSON array only
        match = re.search(r"\[.*\]", raw_output, re.DOTALL)
        if match:
            raw_output = match.group(0)

        quiz = json.loads(raw_output)
        return quiz
    except Exception:
        # fallback if parsing fails
        return [
            {
                "question": "Quiz generation failed",
                "options": [],
                "answer": "N/A",
            }
        ]
