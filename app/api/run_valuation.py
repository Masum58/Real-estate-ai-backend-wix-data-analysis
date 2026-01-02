from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import os
import requests
import traceback
from dotenv import load_dotenv

from app.models.subject_property import SubjectProperty
from app.services.comparable_selector import ComparableSelector
from app.services.feature_builder import FeatureBuilder
from app.ai.prompt_builder import PromptBuilder
from app.services.openai_service import generate_ai_summary

load_dotenv()
router = APIRouter()

RAW_DATA_API_URL = os.getenv("RAW_DATA_API_URL")
CLEAN_DATA_POST_URL = os.getenv("CLEAN_DATA_POST_URL")

if not RAW_DATA_API_URL:
    raise ValueError("RAW_DATA_API_URL missing")

if not CLEAN_DATA_POST_URL:
    raise ValueError("CLEAN_DATA_POST_URL missing")

class ValuationRequest(BaseModel):
    address: str
    bedrooms: int
    bathrooms: int
    square_footage: int
    year_built: int
    condition_score: int
    user_notes: str
    email: EmailStr

class ValuationResponse(BaseModel):
    success: bool
    itemId: str | None
    price_min: int
    price_max: int

def fetch_clean_mls_data():
    resp = requests.get(RAW_DATA_API_URL, timeout=30)
    resp.raise_for_status()
    return resp.json().get("items", [])

@router.post("/run-valuation", response_model=ValuationResponse)
def run_valuation(payload: ValuationRequest):
    try:
        subject = SubjectProperty(**payload.model_dump())

        mls_data = fetch_clean_mls_data()
        if not mls_data:
            raise Exception("MLS data empty")

        selector = ComparableSelector(subject)
        comparables = selector.select(mls_data)
        if not comparables:
            raise Exception("No comparables found")

        features = FeatureBuilder.build(
            comparables=comparables,
            condition_score=subject.condition_score
        )

        prompt = PromptBuilder.build(subject, features)
        ai_summary = generate_ai_summary(prompt)

        wix_payload = {
            "address": subject.address,
            "email": subject.email,
            "price_min": features["price_range"]["min"],
            "price_max": features["price_range"]["max"],
            "summary": ai_summary
        }

        wix_resp = requests.post(
            CLEAN_DATA_POST_URL,
            json=wix_payload,
            timeout=30
        )
        wix_resp.raise_for_status()
        wix_json = wix_resp.json()

        # 🔥 CORRECT ID EXTRACTION
        item_id = (
            wix_json.get("_id")
            or wix_json.get("item", {}).get("_id")
            or wix_json.get("data", {}).get("_id")
        )

        return {
            "success": True,
            "itemId": item_id,
            "price_min": wix_payload["price_min"],
            "price_max": wix_payload["price_max"]
        }

    except Exception as e:
        print("❌ ERROR TRACE:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
