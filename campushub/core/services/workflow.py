from celery import shared_task, chord

# -------------------------------------------------------------
# 1. DUMMY TASKS FOR ISOLATED TESTING
# -------------------------------------------------------------

@shared_task(bind=True)
def dummy_scrape_task(self, club_id):
    """
    Simulates your 'run_club_scrape_task' or 'persist_club_dataset'.
    In a chord, whatever this task returns gets aggregated into a 
    list and passed to the callback task.
    """
    import time
    print(f"[Worker] Starting scrape for club: {club_id}")
    time.sleep(2) # Simulate processing time
    print(f"[Worker] Finished scrape for club: {club_id}")
    
    # This return dictionary gets passed to the callback!
    return {"club_id": club_id, "status": "success"}


@shared_task(bind=True)
def dummy_bulk_email_task(self, results, user_email):
    """
    This is the CALLBACK task.
    It automatically receives 'results' as its first argument, which is 
    a list of the return values from EVERY task in the group.
    """
    print(f"[Worker] All tasks in the group are completed!")
    print(f"[Worker] Received results array: {results}")
    print(f"[Worker] Sending bulk notification email to: {user_email}")
    
    # Mocking Resend behavior
    return "Email successfully deployed"

# -------------------------------------------------------------
# 2. MOCK VIEW / ENTRYPOINT
# -------------------------------------------------------------

def trigger_isolated_workflow(club_ids, user_email):
    """
    This simulates what your Django view will do.
    Instead of looping and calling .apply_async() for each club_id,
    you put them into a chord.
    """
    print(f"[View] Received frontend request to bulk scrape clubs: {club_ids}")
    
    # Step A: Define the "Header" (The group of tasks to run in parallel)
    # We use .s() to create a "Signature", which is an unevaluated task.
    task_signatures_to_run = [dummy_scrape_task.s(c_id) for c_id in club_ids]
    
    # Step B: Define the "Callback" (The task to run after the group finishes)
    callback_signature = dummy_bulk_email_task.s(user_email=user_email)
    
    # Step C: Execute the Chord
    # Syntax is: chord( header_tasks )( callback_task )
    workflow_execution = chord(task_signatures_to_run)(callback_signature)
    
    print(f"[View] Spawned Chord Task ID: {workflow_execution.id}")
    return workflow_execution

# -------------------------------------------------------------
# You can test this manually via python shell:
# >>> from core.services.workflow import trigger_isolated_workflow
# >>> trigger_isolated_workflow([10, 15, 27], "admin@example.com")
# -------------------------------------------------------------
