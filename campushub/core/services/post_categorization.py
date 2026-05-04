from typing import Optional

DEFAULT_POST_CATEGORY = 'Uncategorized'
CATEGORY_KEYWORDS = {
    'Recruitment': ['recruit', 'join', 'membership', 'member', 'register'],
    'Competition': ['competition', 'match', 'tournament', 'contest', 'league'],
    'Event': ['event', 'workshop', 'talk', 'seminar', 'webinar', 'meetup'],
    'Announcement': ['announce', 'announcement', 'launch', 'opening', 'update'],
    'Social': ['party', 'gathering', 'hangout', 'celebration', 'social'],
}


def predict_post_category(caption: Optional[str]) -> str:
    """Return a predicted category label for the post caption.

    This is a placeholder implementation. Replace this with GLINER or
    a more advanced NLP pipeline later.
    """
    caption_text = (caption or '').strip()
    if not caption_text:
        return DEFAULT_POST_CATEGORY

    caption_lower = caption_text.lower()
    for category, terms in CATEGORY_KEYWORDS.items():
        if any(term in caption_lower for term in terms):
            return category

    return DEFAULT_POST_CATEGORY


def assign_category_to_post(post) -> str:
    """Predict category from caption and persist it on the Post record."""
    category = predict_post_category(post.caption)
    post.category = category
    post.save(update_fields=['category'])
    return category
