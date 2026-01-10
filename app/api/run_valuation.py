from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
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
    raise ValueError("RAW_DATA_API_URL missing from environment")

if not CLEAN_DATA_POST_URL:
    raise ValueError("CLEAN_DATA_POST_URL missing from environment")


class ValuationRequest(BaseModel):
    """
    Request model for property valuation.
    Includes location fields for 1-mile radius filtering.
    """
    address: str
    city: str          # For exact city match
    state: str         # For NC/SC cross-state support
    zip_code: str      # For proximity filtering
    bedrooms: int
    bathrooms: int
    square_footage: int
    year_built: int
    condition_score: int  # 1-10 scale
    user_notes: str
    email: EmailStr


class ValuationResponse(BaseModel):
    """
    Response model for property valuation.
    """
    success: bool
    itemId: Optional[str]  # ✅ Compatible with older Python
    price_min: int
    price_max: int


def fetch_clean_mls_data():
    """
    Fetch raw MLS data from Wix database.
    Returns list of property dictionaries.
    """
    resp = requests.get(RAW_DATA_API_URL, timeout=30)
    resp.raise_for_status()
    return resp.json().get("items", [])


@router.post("/run-valuation", response_model=ValuationResponse)
def run_valuation(payload: ValuationRequest):
    """
    Main valuation endpoint.
    
    Process:
    1. Fetch MLS data from Wix
    2. Select comparables within 1-mile radius
    3. Calculate price using distance-based weighting
    4. Generate AI summary
    5. Save to Wix database
    6. Return results with itemId
    """
    try:
        print(f"🔵 Received valuation request for: {payload.address}, {payload.city}, {payload.state} {payload.zip_code}")
        
        # Create subject property object
        subject = SubjectProperty(**payload.model_dump())

        # Fetch raw MLS data
        mls_data = fetch_clean_mls_data()
        if not mls_data:
            raise Exception("MLS data empty - no properties available")
        
        print(f"✅ Fetched {len(mls_data)} MLS records")

        # Select comparables (1-mile radius + filters)
        selector = ComparableSelector(subject)
        comparables = selector.select(mls_data)
        
        if not comparables:
            raise Exception(f"No comparables found for {subject.city}, {subject.state}")
        
        print(f"✅ Selected {len(comparables)} comparables in {subject.city}, {subject.state}")

        # Calculate price features (weighted average)
        features = FeatureBuilder.build(
            comparables=comparables,
            condition_score=subject.condition_score
        )
        
        print(f"✅ Built features - Price range: ${features['price_range']['min']:,} - ${features['price_range']['max']:,}")

        # Generate AI summary
        prompt = PromptBuilder.build(subject, features)
        ai_summary = generate_ai_summary(prompt)
        
        print(f"✅ Generated AI summary")

        # Prepare payload for Wix
        wix_payload = {
            "address": subject.address,
            "city": subject.city,
            "state": subject.state,
            "zipCode": subject.zip_code,  # Note: Wix uses zipCode not zip_code
            "email": subject.email,
            "price_min": features["price_range"]["min"],
            "price_max": features["price_range"]["max"],
            "summary": ai_summary
        }

        # Save to Wix database
        print(f"🔵 Posting to Wix: {CLEAN_DATA_POST_URL}")
        wix_resp = requests.post(
            CLEAN_DATA_POST_URL,
            json=wix_payload,
            timeout=30
        )
        wix_resp.raise_for_status()
        wix_json = wix_resp.json()
        
        print(f"✅ Wix response: {wix_json}")

        # Extract itemId (try multiple possible locations)
        item_id = (
            wix_json.get("_id")
            or wix_json.get("item", {}).get("_id")
            or wix_json.get("data", {}).get("_id")
        )
        
        if not item_id:
            print(f"⚠️ Warning: No item_id found in Wix response")

        # Prepare response
        response_data = {
            "success": True,
            "itemId": item_id,
            "price_min": wix_payload["price_min"],
            "price_max": wix_payload["price_max"]
        }
        
        print(f"✅ Sending response: {response_data}")
        
        # ✅ Return normal response (CORS handled by middleware)
        return response_data

    except requests.exceptions.Timeout:
        error_msg = "Request timeout - external service took too long"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=504, detail=error_msg)
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"External API error: {e.response.status_code} - {e.response.text}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(status_code=502, detail=error_msg)
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(status_code=502, detail=error_msg)
    
    except Exception as e:
        print("❌ ERROR TRACE:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))