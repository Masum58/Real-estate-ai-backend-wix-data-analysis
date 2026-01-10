import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


def post_to_client_backend(payload: Dict) -> Optional[Dict]:
    """
    Send valuation result to Wix clean data collection.
    
    Args:
        payload: Dictionary containing valuation data (address, city, price, summary, etc.)
        
    Returns:
        Wix response dictionary containing itemId and saved data, or None if failed
    """

    url = os.getenv("CLEAN_DATA_POST_URL")  # ✅ Fixed variable name

    if not url:
        print("❌ Error: CLEAN_DATA_POST_URL is not set in environment variables")
        return None

    print(f"🔵 Posting to Wix: {url}")

    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        wix_data = response.json()
        
        # Extract itemId for logging
        item_id = wix_data.get("item", {}).get("_id", "unknown")
        
        print(f"✅ Wix response: {wix_data}")
        print(f"✅ Saved with itemId: {item_id}")
        
        return wix_data  # ✅ Return full response (includes itemId)

    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Wix backend took longer than 30 seconds")
        return None
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to post to Wix: {str(e)}")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None