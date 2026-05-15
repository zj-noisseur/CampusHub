# CampusHub Celery Orchestration Flow

## Complete Task Execution Diagram

```mermaid
graph TD
    Start["orchestrator(club_id, search_limit, max_items, ...)"]
    Start -->|apply_async| Chain["CHAIN: Sequential Execution"]
    
    Chain -->|Task 1| RetrieveJSON["retrieve_json.si(club_id, search_limit, ...)"]
    
    RetrieveJSON -->|fetches Instagram data| Apify["Apify Actor"]
    Apify -->|returns dataset| RetrieveJSONResult["✓ Returns: dataset list"]
    
    RetrieveJSONResult -->|passed to| Task2["TASK 2: process"]
    
    Task2 -->|input: dataset| ProcessStart["process(dataset, club_id, full_sync)"]
    
    ProcessStart -->|iterates| Loop["For each post in dataset"]
    
    Loop -->|step 1| UpdatePost["Post.update_or_create()"]
    UpdatePost -->|step 2| CheckCategory{Post is new OR<br/>category='MISC'?}
    
    CheckCategory -->|YES| EnqueueClass["classify_post.delay(post.id)<br/>(Fire & Forget)"]
    CheckCategory -->|NO| SkipClass["Skip Classification"]
    
    EnqueueClass -->|queued to broker| ClassWorker["[Worker Thread]<br/>classify_post executes<br/>independently"]
    ClassWorker -->|calls ML backend| MLBackend["ML Backend Service<br/>localhost:8001/classify"]
    MLBackend -->|returns| ClassResult["Post.category updated<br/>⚠️ Non-blocking"]
    
    SkipClass -->|continue| ImageLoop["step 3: Collect image URLs"]
    EnqueueClass -->|continue| ImageLoop
    
    ImageLoop -->|for each image| QueueDownload["download_image_worker.s()<br/>added to list"]
    
    QueueDownload -->|accumulate| ImageTasks["image_download_tasks list"]
    
    Loop -->|loop ends| CheckImages{Any images<br/>to download?}
    
    CheckImages -->|YES| ChordSetup["CHORD Setup<br/>Header: image_download_tasks[]<br/>Callback: finalize_workflow"]
    CheckImages -->|NO| NoImages["finalize_club_workflow(club.id, [])<br/>Direct finalization"]
    
    ChordSetup -->|trigger| ChordExecute["Chord(image_tasks)(finalize_callback)"]
    
    ChordExecute -->|parallel execution| ImageWorker1["download_image_worker #1"]
    ChordExecute -->|parallel execution| ImageWorker2["download_image_worker #2"]
    ChordExecute -->|parallel execution| ImageWorkerN["download_image_worker #N"]
    
    ImageWorker1 -->|downloads| Image1["requests.get(url)<br/>saves to filesystem"]
    ImageWorker2 -->|downloads| Image2["requests.get(url)<br/>saves to filesystem"]
    ImageWorkerN -->|downloads| ImageN["requests.get(url)<br/>saves to filesystem"]
    
    Image1 -->|returns| Result1["{'status': 'success',<br/>post_id, path}"]
    Image2 -->|returns| Result2["{'status': 'success',<br/>post_id, path}"]
    ImageN -->|returns| ResultN["{'status': 'error',<br/>post_id, error}"]
    
    Result1 -->|aggregated| Results["Results list<br/>[result1, result2, ..., resultN]"]
    Result2 -->|aggregated| Results
    ResultN -->|aggregated| Results
    
    Results -->|all headers done| Callback["Chord Callback:<br/>finalize_workflow(results, club_id)"]
    
    NoImages -->|immediate| Callback
    
    Callback -->|process results| ValidateResults["Normalize and validate<br/>results list"]
    
    ValidateResults -->|separate| SuccessList["Success results"]
    ValidateResults -->|separate| FailedList["Failed results"]
    
    SuccessList -->|bulk create| BulkCreate["PostImage.objects.bulk_create()"]
    FailedList -->|log| LogFailed["Log failed items"]
    
    BulkCreate -->|update| UpdateClub["club.last_fetched_date = now()<br/>club.posts_count = count()"]
    LogFailed -->|update| UpdateClub
    
    UpdateClub -->|mark complete| UpdateStatus["ClubScrapeStatus.objects.update()<br/>state='SUCCESS'<br/>finished_at=now()"]
    
    UpdateStatus -->|return| FinalResult["{'step': 'complete',<br/>images_saved,<br/>summary}"]
    
    FinalResult -->|WORKFLOW COMPLETE| End["✓ All tasks done<br/>- Posts saved<br/>- Images downloaded<br/>- Categories classified (async)"]
    
    ClassResult -.->|independent path| ClassComplete["✓ Classification task<br/>completes independently"]
    ClassComplete -.->|no callback| NoSync["Does not block workflow"]
    
    style Start fill:#4CAF50,color:#fff
    style Chain fill:#2196F3,color:#fff
    style RetrieveJSON fill:#FF9800,color:#fff
    style ProcessStart fill:#FF9800,color:#fff
    style EnqueueClass fill:#9C27B0,color:#fff
    style ClassWorker fill:#9C27B0,color:#fff
    style ClassComplete fill:#9C27B0,color:#fff
    style ChordSetup fill:#F44336,color:#fff
    style ImageWorker1 fill:#F44336,color:#fff
    style ImageWorker2 fill:#F44336,color:#fff
    style ImageWorkerN fill:#F44336,color:#fff
    style Callback fill:#00BCD4,color:#fff
    style End fill:#4CAF50,color:#fff
    style MLBackend fill:#e74c3c,color:#fff
    style NoSync fill:#9C27B0,color:#fff,stroke-dasharray: 5 5
