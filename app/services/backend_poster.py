import os
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


def post_to_client_backend(payload: Dict) -> bool:
    """
    Send clean data + AI result to client backend in one POST request.
    Returns True if successful, False otherwise.
    """

    url = os.getenv("CLEAN_DATA_POST_API_URL")

    if not url:
        print("CLEAN_DATA_POST_API_URL is not set")
        return False

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        print("POST successful. Status code:", response.status_code)
        return True

    except requests.exceptions.RequestException as e:
        print("POST failed:", str(e))
        return False
