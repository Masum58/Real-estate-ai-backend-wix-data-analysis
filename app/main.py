import os
from dotenv import load_dotenv

load_dotenv()

import requests

from app.models.subject_property import SubjectProperty
from app.services.comparable_selector import ComparableSelector
from app.services.feature_builder import FeatureBuilder
from app.ai.prompt_builder import PromptBuilder
from openai import OpenAI



RAW_DATA_API_URL = os.getenv("RAW_DATA_API_URL")
CLEAN_DATA_POST_URL = os.getenv("CLEAN_DATA_POST_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---- ADD THIS BLOCK HERE ----
if not RAW_DATA_API_URL:
    raise ValueError("RAW_DATA_API_URL is missing in .env file")

if not CLEAN_DATA_POST_URL:
    raise ValueError("CLEAN_DATA_POST_URL is missing in .env file")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing in .env file")
# -----------------------------


def fetch_clean_mls_data():
    response = requests.get(RAW_DATA_API_URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("items", [])



def post_result_to_wix(payload: dict):
    response = requests.post(
        CLEAN_DATA_POST_URL,
        json=payload,
        timeout=30
    )
    response.raise_for_status()


def generate_ai_summary(prompt: str) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful real estate assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()


def main():
    # Example subject property (later this comes from Wix POST)
    subject = SubjectProperty(
        address="User Provided Address",
        bedrooms=4,
        bathrooms=3,
        square_footage=2800,
        year_built=2015,
        condition_score=7,
        user_notes="Light rehab",
        email="user@example.com"
    )

    # Step 1: Fetch MLS data
    mls_data = fetch_clean_mls_data()

    # Step 2: Select comparables
    selector = ComparableSelector(subject)
    comparables = selector.select(mls_data)

    if not comparables:
        raise RuntimeError("No comparable properties found")

    # Step 3: Build AI features
    features = FeatureBuilder.build(
        comparables=comparables,
        condition_score=subject.condition_score
    )

    # Step 4: Build AI prompt
    prompt = PromptBuilder.build(subject, features)

    # Step 5: Generate AI summary
    ai_summary = generate_ai_summary(prompt)

    # Final payload for Wix
    result_payload = {
        "address": subject.address,
        "email": subject.email,
        "price_min": features["price_range"]["min"],
        "price_max": features["price_range"]["max"],
        "summary": ai_summary
    }

    # Step 6: Send to Wix
    post_result_to_wix(result_payload)

    print("Phase-1.5 pipeline executed successfully.")
    print("Fetched MLS data:", len(mls_data))
    print("Selected comparable properties:", len(comparables))
    print("Features built:", features)
    print("AI Summary:", ai_summary[:100])



if __name__ == "__main__":
    main()
