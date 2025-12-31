import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing in .env file")


def generate_ai_summary(prompt: str) -> str:
    """
    Calls OpenAI API and returns a clean AI-generated summary.
    """

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional real estate valuation assistant. "
                    "Never mention MLS addresses, listing IDs, or specific properties. "
                    "Provide a clear, neutral market-based explanation."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()
