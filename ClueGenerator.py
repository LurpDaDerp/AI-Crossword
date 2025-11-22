import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
client = OpenAI()

print("ENV KEY:", os.getenv("OPENAI_API_KEY"))


def generate_clues(horizontal_words, vertical_words):
    answers = {
        "horizontal": horizontal_words,
        "vertical": vertical_words,
    }

    prompt = f"""
You generate crossword clues.

INPUT WORDS:
{json.dumps(answers)}

OUTPUT:
Return ONLY valid JSON:
{{
  "horizontal": {{ "WORD": "clue", ... }},
  "vertical":   {{ "WORD": "clue", ... }}
}}

Rules:
- 3–7 word English clues for these crossword words.
- Never include the answer word.
- No markdown, no text outside JSON.
"""

    resp = client.responses.create(
        model="gpt-5-nano",
        input=prompt,
        max_output_tokens=300,
        reasoning={ "effort": "minimal" },
    )

    raw = resp.output_text

    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("JSON not found in output.")

    return json.loads(raw[start:end + 1])
