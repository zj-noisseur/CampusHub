from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from transformers import pipeline
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    logger.info("Booting up: Loading cross-encoder/nli-deberta-v3-small into RAM...")
    
    # Suppress transformers warnings
    from transformers import logging as hf_logging
    hf_logging.set_verbosity_error()
    
    # Store the model in app.state instead of a global dict
    app.state.classifier = pipeline(
        "zero-shot-classification",
        model="cross-encoder/nli-deberta-v3-small"
    )
    
    logger.info("Model loaded successfully. Ready for traffic.")
    
    yield # Server is running
    
    # --- SHUTDOWN LOGIC ---
    logger.info("Shutting down: Clearing memory...")
    del app.state.classifier

app = FastAPI(title="CampusHub ML Backend Service", lifespan=lifespan)

CATEGORIES = {
    "RECRUITMENT": "Recruitment",
    "COMPETITION": "Competition",
    "WORKSHOP": "Workshop",
    "INDUSTRIAL_VISIT": "Industrial Visit",
    "ANNOUNCEMENT": "Announcement",
    "PAST_EVENT": "Past Event",
    "MISC": "Miscellaneous"
}

class ClassificationRequest(BaseModel):
    text: str
    candidate_labels: Optional[List[str]] = None

class ClassificationResponse(BaseModel):
    label: str
    category_key: str
    score: float

@app.get("/health")
async def health_check(request: Request):
    # Check if the classifier exists in app state
    is_loaded = hasattr(request.app.state, "classifier")
    return {"status": "healthy" if is_loaded else "booting", "model_loaded": is_loaded}

@app.get("/categories")
async def get_categories():
    return CATEGORIES

@app.post("/classify", response_model=ClassificationResponse)
async def classify_text(request: Request, classification_data: ClassificationRequest):
    """
    Note: We now inject 'request: Request' to access app.state
    """
    text = classification_data.text
    if not text.strip():
        raise HTTPException(status_code=400, detail="Empty text provided")
    
    classifier_labels = classification_data.candidate_labels or [
        label for key, label in CATEGORIES.items() if key not in ["MISC", "PAST_EVENT"]
    ]

    try:
        # Access the classifier from the app state
        classifier = request.app.state.classifier
        
        result = classifier(text, candidate_labels=classifier_labels)
        
        # Grab the top results (index 0)
        top_label = result['labels']
        top_score = result['scores']
        
        category_key = next(
            (k for k, v in CATEGORIES.items() if v == top_label), 
            "MISC"
        )
        
        return ClassificationResponse(
            label=top_label, 
            category_key=category_key, 
            score=top_score
        )
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Using the string reference "main:app" is required for reload and lifespan reliability
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)