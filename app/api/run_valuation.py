from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
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

@router.options("/run-valuation")
async def run_valuation_options():
    """Handle preflight CORS requests"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "600"
        }
    )

@router.post("/run-valuation", response_model=ValuationResponse)
def run_valuation(payload: ValuationRequest):
    try:
        print(f"🔵 Received valuation request for: {payload.address}")
        
        subject = SubjectProperty(**payload.model_dump())

        mls_data = fetch_clean_mls_data()
        if not mls_data:
            raise Exception("MLS data empty")
        
        print(f"✅ Fetched {len(mls_data)} MLS records")

        selector = ComparableSelector(subject)
        comparables = selector.select(mls_data)
        if not comparables:
            raise Exception("No comparables found")
        
        print(f"✅ Selected {len(comparables)} comparables")

        features = FeatureBuilder.build(
            comparables=comparables,
            condition_score=subject.condition_score
        )
        
        print(f"✅ Built features - Price range: ${features['price_range']['min']:,} - ${features['price_range']['max']:,}")

        prompt = PromptBuilder.build(subject, features)
        ai_summary = generate_ai_summary(prompt)
        
        print(f"✅ Generated AI summary")

        wix_payload = {
            "address": subject.address,
            "email": subject.email,
            "price_min": features["price_range"]["min"],
            "price_max": features["price_range"]["max"],
            "summary": ai_summary
        }

        print(f"🔵 Posting to Wix: {CLEAN_DATA_POST_URL}")
        wix_resp = requests.post(
            CLEAN_DATA_POST_URL,
            json=wix_payload,
            timeout=30
        )
        wix_resp.raise_for_status()
        wix_json = wix_resp.json()
        
        print(f"✅ Wix response: {wix_json}")

        # 🔥 CORRECT ID EXTRACTION
        item_id = (
            wix_json.get("_id")
            or wix_json.get("item", {}).get("_id")
            or wix_json.get("data", {}).get("_id")
        )
        
        if not item_id:
            print(f"⚠️ Warning: No item_id found in Wix response")

        response_data = {
            "success": True,
            "itemId": item_id,
            "price_min": wix_payload["price_min"],
            "price_max": wix_payload["price_max"]
        }
        
        print(f"✅ Sending response: {response_data}")
        
        return JSONResponse(
            content=response_data,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
            }
        )

    except requests.exceptions.RequestException as e:
        error_msg = f"External API error: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(status_code=502, detail=error_msg)
    
    except Exception as e:
        print("❌ ERROR TRACE:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))