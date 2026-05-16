from typing import Optional, List, Dict
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def predict_post_category(caption: Optional[str]) -> str:
    """Return a predicted category label for the post caption.
    
    This implementation calls the decoupled ML Backend microservice 
    for zero-shot classification.
    """
    caption_text = (caption or '').strip()
    if not caption_text:
        return 'MISC'

    # To avoid circular imports, we import Post here
    from core.models import Post
    
    # Get configuration from settings, default to localhost for development
    service_url = getattr(settings, 'ML_BACKEND_URL', 'http://localhost:8001')
    endpoint = f"{service_url.rstrip('/')}/classify"
    
    try:
        # We no longer need to send candidate_labels as the server knows them
        payload = {"text": caption_text}
        
        response = requests.post(endpoint, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        category_key = data.get('category_key')
        
        # Validation: Ensure the key actually exists in our Django model
        from core.models import Post
        valid_keys = [k for k, v in Post.CATEGORY_CHOICES]
        
        if category_key in valid_keys:
            return category_key
        
        logger.warning(f"ML Backend returned unknown category key: {category_key}")
        return 'MISC'
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling ML Backend at {endpoint}: {e}")
        return 'MISC'
    except Exception as e:
        logger.error(f"Unexpected error during classification: {e}")
        return 'MISC'


def predict_is_event(caption: str) -> Optional[bool]:
    """Predict if a post is an upcoming event using Step 1 (Temporal Classification)."""
    caption_text = (caption or '').strip()
    if not caption_text:
        return False

    service_url = getattr(settings, 'ML_BACKEND_URL', 'http://localhost:8001')
    endpoint = f"{service_url.rstrip('/')}/classify"
    
    # Candidate labels for Step 1
    # We use a premise-hypothesis approach by phrasing them as clear choices
    candidate_labels = [
        "upcoming event or recruitment with a deadline", 
        "past event recap or general announcement without a deadline"
    ]
    
    try:
        payload = {
            "text": caption_text,
            "candidate_labels": candidate_labels
        }
        
        response = requests.post(endpoint, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        top_label = data.get('label')
        
        # If the top label is the one describing an upcoming event, return True
        return top_label == candidate_labels[0]
        
    except Exception as e:
        logger.error(f"Error during Step 1 Temporal Classification: {e}")
        return None


def assign_category_to_post(post) -> str:
    """Predict category from caption and persist it on the Post record."""
    category_key = predict_post_category(post.caption)
    post.category = category_key
    post.save(update_fields=['category'])
    
    # Get the human-readable label for the response
    label = dict(post._meta.get_field('category').choices).get(category_key, category_key)
    print(f"Predicted Category for Post {post.short_code}: {label} ({category_key})")
    
    return label


def assign_event_status_to_post(post) -> Optional[bool]:
    """Predict event status and persist it on the Post record."""
    is_event = predict_is_event(post.caption)
    post.is_event = is_event
    post.save(update_fields=['is_event'])
    return is_event


if __name__ == "__main__":
    # Test cases to verify classification logic
    test_captions = [
        "⚡Linux Workshop 2026⚡ 📍 FAIE AI Design Lab 🗓 29th May 2026 ⏰ 9:00AM – 4:00PM 🎟 FREE for IEEE members 💰 RM5 for non-members ⚠️ Limited slots available Bring your laptop & secure your spot now! #IEEE #Workshop #LinuxWorkshop",
        "Ever wondered how platforms like JobStreet actually work behind the scenes? 👀 Here’s your chance to experience it firsthand! 📅 Date: 14th May 2026 ⏰ Time: 11:30 AM – 5:30 PM 📍 Venue: JobStreet by SEEK - Malaysia, Level 20 Menara, AIA Cap Square, 10, Jalan Munshi Abdullah, City Centre, 50100 Kuala Lumpur, Wilayah Persekutuan Kuala Lumpur ✨ What you’ll gain: • Insights into how a leading job platform operates • Exposure to real industry environment • Better understanding of career pathways • A chance to learn directly from professionals Open to FCI students; Year 2 and Final Year students are highly encouraged to join! ⚠️ Limited slots (first come, first served!) Attire: Smart casual (no shorts, slippers, or inappropriate wear) Essential: IC/Passport Don’t miss this opportunity to explore the industry up close — sign up now! Register here: https://forms.gle/xW1ALpQdCG3bju1u8",
    ]

    import os
    import django
    import sys
    
    # Add the project root to sys.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campushub.settings')
    django.setup()

    for caption in test_captions:
        category_key = predict_post_category(caption)
        print(f"CAPTION: {caption[:50]}...")
        print(f"PREDICTED KEY: {category_key}\n")