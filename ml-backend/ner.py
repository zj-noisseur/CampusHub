import spacy
from spacy.tokens import Span
from spacy.language import Language

TARGET_LABELS = {"FAC", "GPE", "LOC", "VENUE"}

@Language.component("address_consolidator")
def address_consolidator(doc):
    location_ents = [ent for ent in doc.ents if ent.label_ in TARGET_LABELS]
    if not location_ents:
        return doc

    consolidated = []
    current_start = location_ents[0].start
    current_end = location_ents[0].end

    for next_ent in location_ents[1:]:
        gap = doc[current_end:next_ent.start]
        # Bridge gaps with common separators, no newlines allowed to prevent merging across blocks
        if (all(c.isalnum() or c in ",.-# " for c in gap.text.strip()) or gap.text.strip() == "") and "\n" not in gap.text:
            current_end = next_ent.end
        else:
            consolidated.append(Span(doc, current_start, current_end, label="VENUE"))
            current_start = next_ent.start
            current_end = next_ent.end

    consolidated.append(Span(doc, current_start, current_end, label="VENUE"))

    # Filtering Logic
    final_venues = []
    # to add the name of the club itself as part of the exclusion keywords
    EXCLUSION_KEYWORDS = {"ic", "passport", "ieee", "student", "attire", "fees", "Information Technology and Media Division", "CLSC"}
    
    for venue in consolidated:
        text_low = venue.text.lower().strip()
        
        # 1. Skip if starts with hashtag or is in exclusion list
        if text_low.startswith("#") or any(kw in text_low for kw in EXCLUSION_KEYWORDS):
            continue
            
        # 2. Heuristic: Keep if it has spatial context or is preceded by a marker
        prev_token = doc[max(0, venue.start - 1)]
        markers = ["at", "in", "venue", "location", "📍", "Location: "]
        is_preceded_by_marker = prev_token.lower_ in markers or prev_token.text in markers
        
        if len(venue.text) >= 3 or is_preceded_by_marker:
             final_venues.append(venue)

    other_ents = [ent for ent in doc.ents if ent.label_ not in TARGET_LABELS]
    doc.ents = spacy.util.filter_spans(other_ents + final_venues)
    return doc

@Language.component("date_time_consolidator")
def date_time_consolidator(doc):
    TIME_LABELS = {"DATE", "TIME"}

    time_ents = [ent for ent in doc.ents if ent.label_ in TIME_LABELS]
    if not time_ents:
        return doc

    consolidated = []
    current_start = time_ents[0].start
    current_end = time_ents[0].end
    current_label = time_ents[0].label_

    for next_ent in time_ents[1:]:
        # Lookahead: absorb punctuation including opening brackets
        while current_end < len(doc) and doc[current_end].text in ["(", "[", ",", "."]:
            current_end += 1

        gap = doc[current_end:next_ent.start]
        has_line_break = any(lb in gap.text for lb in ["\n", "\r", "\u2028", "\u2029"])
        
        # Bridge if labels match OR if merging DATE/TIME, and the gap is just typical separators/brackets
        is_bridgeable = (all(c in "()[]–-—, " for c in gap.text.strip()) or gap.text.strip() == "") and not has_line_break
        
        if is_bridgeable:
            current_end = next_ent.end
            # Prioritize DATE label if we merge DATE and TIME
            if next_ent.label_ == "DATE":
                current_label = "DATE"
        else:
            # Before closing current, absorb trailing punctuation
            while current_end < len(doc) and doc[current_end].text in [")", "]", ",", "."]:
                current_end += 1
            
            consolidated.append(Span(doc, current_start, current_end, label=current_label))
            current_start = next_ent.start
            current_end = next_ent.end
            current_label = next_ent.label_

    # Final punctuation absorption
    while current_end < len(doc) and doc[current_end].text in [")", "]", ",", "."]:
        current_end += 1
    consolidated.append(Span(doc, current_start, current_end, label=current_label))
  
    other_ents = [ent for ent in doc.ents if ent.label_ not in TIME_LABELS]
    doc.ents = spacy.util.filter_spans(other_ents + consolidated)
    return doc


@Language.component("token_entity_sanitizer")
def token_entity_sanitizer(doc):
    MISCLASSIFIED_KEYWORDS = {"location", "venue", "attire", "essential", "fees", "📍", "⏰"}
    
    # Clean up token-level metadata markers
    for token in doc:
        if token.text.lower().strip() in MISCLASSIFIED_KEYWORDS:
            token.ent_type_ = ""
            
    valid_ents = []
    for ent in doc.ents:
        clean_tokens = [t for t in ent if t.text.lower().strip() not in MISCLASSIFIED_KEYWORDS]
        if clean_tokens:
            valid_ents.append(Span(doc, clean_tokens[0].i, clean_tokens[-1].i + 1, label=ent.label_))
            
    doc.ents = spacy.util.filter_spans(valid_ents)
    return doc

patterns = [
    {
        "label": "FAC", 
        "pattern": [
            {"POS": "PROPN", "OP": "+"}, 
            {"LOWER": {"IN": ["lab", "laboratory", "room", "theatre", "hall", "center", "centre", "studio"]}}
        ]
    },
    {"label": "LOC", "pattern": [{"TEXT": {"REGEX": r"(?i)^fci[-–—]?$"}}]},
    {"label": "LOC", "pattern": [{"TEXT": {"REGEX": r"(?i)^faie[-–—]?$"}}]},
    {"label": "LOC", "pattern": [{"TEXT": {"REGEX": r"(?i)^fom[-–—]?$"}}]},
    {"label": "LOC", "pattern": [{"TEXT": {"REGEX": r"(?i)^fcm[-–—]?$"}}]},
    {"label": "LOC", "pattern": [{"TEXT": {"REGEX": r"(?i)^mmu[-–—]?$"}}]},
    {
        "label": "FAC",
        "pattern": [
            {"TEXT": {"REGEX": r"^[A-Z]{2,4}$"}},                       # "CLCR"
            {"TEXT": {"REGEX": r"^[-–—]$"}, "OP": "?"},                 # Optional dash
            {"TEXT": {"REGEX": r"^\d{3,4}[A-Z]?$"}}                     # "3045"
        ]
    },
    {"label": "LOC", "pattern": [{"LOWER": "block"}, {"POS": "PROPN"}]},
    {"label": "LOC", "pattern": [{"LOWER": "block"}, {"IS_DIGIT": True}]},
    {"label": "TIME", "pattern": [{"TEXT": {"REGEX": r"^\d{1,2}:\d{2}(?:[AP]M)?$"}}]},
    {"label": "DATE", "pattern": [{"TEXT": {"REGEX": r"^\d{1,2}(?:st|nd|rd|th)$"}}]}
]

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_trf")
        except OSError:
            import subprocess
            import sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_trf"], check=True)
            _nlp = spacy.load("en_core_web_trf")

        # Initialize pipeline components
        ruler = _nlp.add_pipe("entity_ruler", after="ner")
        ruler.add_patterns(patterns)
        _nlp.add_pipe("token_entity_sanitizer", after="entity_ruler")
        _nlp.add_pipe("address_consolidator", after="token_entity_sanitizer")
        _nlp.add_pipe("date_time_consolidator", last=True)
    return _nlp

def extract_details_from_text(text: str) -> dict:
    if not text:
        return {"venue": "", "date": "", "time": "", "link": ""}
    
    nlp = get_nlp()
    doc = nlp(text.replace("\u2028", "\n").replace("\u2029", "\n"))
    
    venues = list(set([ent.text.replace('\n', ' ').strip() for ent in doc.ents if ent.label_ == "VENUE"]))
    dates = list(set(ent.text.replace('\n', ' ').strip() for ent in doc.ents if ent.label_ == "DATE"))
    times = list(set(ent.text.replace('\n', ' ').strip() for ent in doc.ents if ent.label_ == "TIME"))
    links = [token.text for token in doc if token.like_url]
    
    unique_venues = [v for v in venues if not any(v != parent and v in parent for parent in venues)]
    
    return {
        "venue": unique_venues[0] if unique_venues else "",
        "date": dates[0] if dates else "",
        "time": times[0] if times else "",
        "link": links[0] if links else ""
    }