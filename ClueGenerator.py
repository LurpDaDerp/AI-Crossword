import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_clues(horizontal_words, vertical_words):
    answers = {
        "horizontal": horizontal_words,
        "vertical": vertical_words,
    }

    prompt = f"""
    You are writing crossword clues
    Input JSON has two lists: horizontal and vertical words
    Return ONLY JSON with same keys, but each word mapped to a clue

    Format:
    {{
    "horizontal": {{ "word": "clue" }},
    "vertical":   {{ "word": "clue" }}
    }}

    Clues must be in English, 3–7 words
    Do NOT include the answer word or related forms
    Include some fill-in-the-blank clues using "____" in the middle of a phrase that make sense
    Return ONLY JSON, no explanation

    Input JSON: {json.dumps(answers)}
        """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7,
    )

    text = resp.choices[0].message.content.strip()
    return json.loads(text)
