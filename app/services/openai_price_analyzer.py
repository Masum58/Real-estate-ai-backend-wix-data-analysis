import os
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_price_with_openai(ai_input: Dict) -> Dict:
    """
    Call OpenAI to generate price range and summary.
    Must return the same structure as local analyzer.
    """

    comparables: List[Dict] = ai_input["comparables"]

    # Keep payload minimal and safe
    compact_comps = [
        {
            "beds": p.get("bedrooms"),
            "baths": p.get("bathrooms"),
            "sqft": p.get("areaSqft"),
            "price": p.get("price"),
            "yearBuilt": p.get("yearBuilt"),
            "conditionScore": p.get("conditionScore"),
        }
        for p in comparables
    ]

    prompt = f"""
You are a real estate pricing assistant.

Rules:
- Do not mention MLS.
- Do not mention addresses.
- Do not mention listing IDs.
- Do not mention agents.
- Use neutral language only.
- Output must be JSON only.

Input:
Comparable properties data:
{compact_comps}

Task:
1) Estimate a reasonable price range.
2) Return a short, human-readable summary.

Output JSON format exactly:
{{
  "price_min": number,
  "price_max": number,
  "summary": string
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a careful, compliant pricing assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    try:
        return eval(content)
    except Exception:
        return {
            "price_min": None,
            "price_max": None,
            "summary": "Unable to generate price estimate at this time."
        }
