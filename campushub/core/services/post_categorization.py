from typing import Optional, List, Dict
import logging
import requests
import re
from django.conf import settings

logger = logging.getLogger(__name__)

from requests.exceptions import RequestException

def predict_post_category(caption: Optional[str], raise_on_error: bool = False) -> str:
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
        
        response = requests.post(endpoint, json=payload, timeout=60)
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
        
    except RequestException as e:
        logger.error(f"Error calling ML Backend at {endpoint}: {e}")
        if raise_on_error:
            raise e
        return 'MISC'
    except Exception as e:
        logger.error(f"Unexpected error during classification: {e}")
        if raise_on_error:
            raise e
        return 'MISC'


def condense_caption(text: str) -> str:
    """Extract only the most semantically relevant lines for classification."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < 10:
        return "\n".join(lines)

    # 1. Keep the Hook (Title/Intro)
    condensed = lines[:3]
    
    # 2. Extract structural signals (Middle)
    # These are high-probability markers for event details
    markers = ['date:', 'time:', 'venue:', 'location:', 'register', 'sign up', 'rsvp', 'join', 'link', 'http', 'deadline', 'fee', 'luma', 'free']
    emoji_pattern = r'[📅⏰📍⏳🎟💰⚠️✨🔗]'
    
    for line in lines[3:-2]:
        if any(m in line.lower() for m in markers) or re.search(emoji_pattern, line):
            condensed.append(line[:250]) # Trim very long lines
    
    # 3. Keep the CTA (End)
    condensed.extend(lines[-2:])
    
    # De-duplicate while preserving order
    seen = set()
    final_lines = []
    for l in condensed:
        if l not in seen:
            final_lines.append(l)
            seen.add(l)
            
    return "\n".join(final_lines)


def predict_is_event(caption: str, raise_on_error: bool = False) -> Optional[bool]:
    """Predict if a post is an upcoming event using Step 1 (Temporal Classification)."""
    original_text = (caption or '').strip()
    if not original_text:
        return False

    # Condense the text to focus on structural signals (Date, Venue, CTA)
    caption_text = condense_caption(original_text)

    service_url = getattr(settings, 'ML_BACKEND_URL', 'http://localhost:8001')
    endpoint = f"{service_url.rstrip('/')}/classify"
    
    # Candidate labels for Step 1
    # We use a premise-hypothesis approach by phrasing them as clear choices
    cta_keywords = ["take part", "participate", "register", "sign up", "RSVP", "apply now", "join us", "recruitment", "recruit"]
    template = f'This post is about'
    
    # 1. NEGATIVE BYPASS (Exclusion)
    # If these keywords are present, it's likely a past event recap or general info
    negative_markers = ["recap", "highlights", "throwback", "memory", "successful event", "thank you to all", "stay tuned for more", "congratulations", "well done"]
    found_negative = next((k for k in negative_markers if k.lower() in original_text.lower()), None)
    
    if found_negative:
        logger.info(f"Step 1: Negative bypass triggered by keyword '{found_negative}'")
        return False

    # 2. POSITIVE BYPASS (Inclusion)
    # If these keywords are present (and no negative ones were found above)
    strong_markers = cta_keywords + ["date", "venue", "location", "deadline", "limited slots", "luma", "form"]
    found_positive = next((k for k in strong_markers if k.lower() in original_text.lower()), None)
    
    if found_positive:
        # HIGH-CONFIDENCE BYPASS: Skip ML if we see a "smoking gun" event marker
        logger.info(f"Step 1: Positive bypass triggered by keyword '{found_positive}'")
        return True

    template = f'This post is about'
    candidate_labels = [
        "promoting an upcoming industrial visit, hackathon, competition, workshop or recruitment openings for committee positions for students to take part, participate in or register for", 
        "a recap of a past event, a general announcement, or purely informational news"
    ]
    
    try:
        payload = {
            "text": caption_text,
            "candidate_labels": [f"{template} {candidate_labels[0]}", f"{template} {candidate_labels[1]}"]
        }
        
        response = requests.post(endpoint, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        top_label = data.get('label')
        
        # If the top label is the one describing an upcoming event, return True
        return top_label == candidate_labels[0]
        
    except RequestException as e:
        logger.error(f"Error during Step 1 Temporal Classification: {e}")
        if raise_on_error:
            raise e
        return None
    except Exception as e:
        logger.error(f"Unexpected error during Step 1 Temporal Classification: {e}")
        if raise_on_error:
            raise e
        return None


def assign_category_to_post(post, raise_on_error: bool = False) -> str:
    """Predict category from caption and persist it on the Post record."""
    category_key = predict_post_category(post.caption, raise_on_error=raise_on_error)
    post.category = category_key
    post.save(update_fields=['category'])
    
    # Get the human-readable label for the response
    label = dict(post._meta.get_field('category').choices).get(category_key, category_key)
    print(f"Predicted Category for Post {post.short_code}: {label} ({category_key})")
    
    return label


def assign_event_status_to_post(post, raise_on_error: bool = False) -> Optional[bool]:
    """Predict event status and persist it on the Post record."""
    is_event = predict_is_event(post.caption, raise_on_error=raise_on_error)
    post.is_event = is_event
    post.save(update_fields=['is_event'])

    if is_event and not post.event:
        from core.models import Event
        from django.utils import timezone
        event = Event.objects.create(
            club=post.club,
            title=f"{post.club.name} Event",
            event_date=timezone.now()  # Provide a default to satisfy NOT NULL constraint
        )
        post.event = event
        post.is_primary_event_post = True
        post.save(update_fields=['event', 'is_primary_event_post'])

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