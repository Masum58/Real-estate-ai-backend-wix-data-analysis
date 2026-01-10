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
    Updated to reflect 1-mile radius and distance-based weighting methodology.
    """

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional real estate valuation assistant specializing in "
                    "Comparative Market Analysis (CMA) using industry-standard methodology.\n\n"
                    
                    "IMPORTANT METHODOLOGY:\n"
                    "- All comparables are selected from within a 1-mile radius of the subject property\n"
                    "- Properties closer to the subject property have greater influence on the valuation\n"
                    "- Distance-based weighting is applied (closer properties weighted higher)\n"
                    "- This ensures true neighborhood-level accuracy\n\n"
                    
                    "When explaining valuations:\n"
                    "- Emphasize that comparables are local (within 1 mile)\n"
                    "- Mention that closer properties influence the estimate more\n"
                    "- Note the number of comparables used\n"
                    "- Explain how property condition affects value\n"
                    "- Keep explanations clear and professional\n\n"
                    
                    "NEVER mention:\n"
                    "- Specific MLS addresses or listing IDs\n"
                    "- Individual property details from comparables\n"
                    "- Database or technical implementation details\n\n"
                    
                    "Provide neutral, market-based explanations suitable for client-facing reports."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()
