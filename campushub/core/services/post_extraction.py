import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

from requests.exceptions import RequestException

def extract_details(text: str, raise_on_error: bool = False) -> dict:
    """Extract details (venue, date, time, link) from text by querying the ML microservice backend."""
    caption_text = (text or '').strip()
    if not caption_text:
        return {"venue": "", "date": "", "time": "", "link": ""}

    # Get configuration from settings, default to localhost for development
    service_url = getattr(settings, 'ML_BACKEND_URL', 'http://localhost:8001')
    endpoint = f"{service_url.rstrip('/')}/extract"

    try:
        payload = {"text": caption_text}
        response = requests.post(endpoint, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(f"Error calling ML Backend extraction at {endpoint}: {e}")
        if raise_on_error:
            raise e
        return {"venue": "", "date": "", "time": "", "link": ""}
    except Exception as e:
        logger.error(f"Unexpected error calling ML Backend extraction at {endpoint}: {e}")
        if raise_on_error:
            raise e
        return {"venue": "", "date": "", "time": "", "link": ""}

if __name__ == "__main__":
    # Test case to verify classification logic when running directly
    test_caption = "⚡Linux Workshop 2026⚡ 📍 FAIE AI Design Lab 🗓 29th May 2026 ⏰ 9:00AM – 4:00PM"
    print(f"Testing local proxy with text: {test_caption}")
    print(f"Result: {extract_details(test_caption)}")