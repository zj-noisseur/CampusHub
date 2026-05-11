# Task Architecture

The Celery workflow in `campushub/core/services/tasks.py` uses a structured arrangement of **Chains** and **Chords** to manage parallel image processing and sequential data fetching.

## Celery Workflow Diagram

```mermaid
graph TD
    subgraph "Orchestration Layer (Chain)"
        A[orchestrator] --> B[retrieve_json]
        B --> C[process]
    end

    subgraph "Parallel Processing Layer (Chord)"
        C --> D{Chord Header}
        D --> E1[download_image_worker 1]
        D --> E2[download_image_worker 2]
        D --> E3[download_image_worker n...]
        
        E1 --> F[Chord Callback]
        E2 --> F
        E3 --> F
        
        F --> G[finalize_workflow]
    end

    subgraph "Database & Notification"
        G --> H[Update DB Scrape Status]
        G --> I[Send Completion Notification]
    end

    style D fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#f9f,stroke:#333,stroke-width:2px
```

## Logic Explanation

### 1. The Chain (Orchestrator)
The workflow starts with a `chain` that ensures the data is first retrieved from the external source (`retrieve_json`) before being passed to the `process` task. This ensures the input for processing is available.

### 2. The Chord (Image Processing)
Within the `process` task, the system identifies all image URLs that need to be downloaded. 
*   **Header (Parallel Group)**: A list of `download_image_worker` signatures is created. Celery executes these in parallel across available workers to maximize performance.
*   **Callback (Synchronization)**: The `chord` ensures that `finalize_workflow` is triggered **only after every single image download task has completed**. It receives the results from all workers as a list.

### 3. Finalization
The `finalize_workflow` task acts as a cleanup and reporting phase, ensuring the database records are consistent and the user is notified of the results.
