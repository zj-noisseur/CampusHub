# CampusHub ML Backend

This service provides AI-driven text classification for CampusHub posts using a zero-shot classification model.

## Classification Logic

The `/classify` endpoint handles text classification following the workflow below:

```mermaid
graph TD
    A[Receive Text] --> B{Empty Text?}
    B -- Yes --> C[400 Error]
    B -- No --> D[Prepare Labels]
    D --> E[Exclude MISC & PAST_EVENT]
    E --> F[Run Zero-Shot Classifier]
    F --> G[Extract Top Prediction]
    G --> H[Map Label back to Key]
    H --> I[Return JSON Response]
```

### Key Features
- **Zero-Shot Classification**: Uses `cross-encoder/nli-deberta-v3-small` to categorize text without specific retraining.
- **Authoritative Categories**: The backend defines the source of truth for all categories used across the CampusHub ecosystem.
- **Smart Exclusion**: Forces the AI to pick a meaningful category by excluding generic types during the classification phase.
