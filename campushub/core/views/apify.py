from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

url = "https://api.apify.com/v2/acts"

def list_actors(): 
    headers = {
    'Accept': 'application/json',
    'Authorization': f"Bearer {os.getenv('APIFY_API_KEY')}"
    }

    response = requests.request("GET", url, headers=headers)

    return (response.text)

def list_actor_runs(actorId):
    headers = {
    'Accept': 'application/json',
    'Authorization': f"Bearer {os.getenv('APIFY_API_KEY')}"
    }

    request_url = f"{url}/{actorId}/runs"
    response  = requests.request("GET", request_url, headers=headers)
    return (response.text)

def run_actor_sync(actorId, input_payload, timeout=300, memory=None, max_items=None, max_total_charge_usd=None):
    """
    Run an actor synchronously and return its output.

    :param actorId: The ID of the actor to run.
    :param input_payload: The input payload for the actor.
    :param timeout: Timeout for the run in seconds (default: 300).
    :param memory: Memory limit for the run in MB (optional).
    :param max_items: Maximum number of dataset items to charge for (optional).
    :param max_total_charge_usd: Maximum cost of the run in USD (optional).
    :return: The output of the actor run.
    """
    headers = {
        'Accept': 'application/json',
        'Authorization': f"Bearer {os.getenv('APIFY_API_KEY')}"
    }

    params = {
        'timeout': timeout,
        'memory': memory,
        'maxItems': max_items,
        'maxTotalChargeUsd': max_total_charge_usd
    }

    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}

    request_url = f"{url}/{actorId}/run-sync"
    response = requests.post(request_url, headers=headers, json=input_payload, params=params)

    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to run actor: {response.status_code} - {response.text}")

def run_actor_sync_get_dataset_items(actorId, input_payload, timeout=None, memory=None, max_items=None, max_total_charge_usd=None, format="json", clean=False, offset=0, limit=None, fields=None, omit=None):
    """
    Run an actor synchronously and retrieve dataset items.

    :param actorId: The ID of the actor to run.
    :param input_payload: The input payload for the actor.
    :param timeout: Timeout for the run in seconds (set to None for now).
    :param memory: Memory limit for the run in MB (optional).
    :param max_items: Maximum number of dataset items to charge for (optional).
    :param max_total_charge_usd: Maximum cost of the run in USD (optional).
    :param format: Format of the dataset items (default: "json").
    :param clean: Whether to return only non-empty items and skip hidden fields (default: False).
    :param offset: Number of items to skip at the start (default: 0).
    :param limit: Maximum number of items to return (optional).
    :param fields: Comma-separated list of fields to include in the output (optional).
    :param omit: Comma-separated list of fields to omit from the output (optional).
    :return: The dataset items from the actor run.
    """
    headers = {
        'Accept': 'application/json',
        'Authorization': f"Bearer {os.getenv('APIFY_API_KEY')}"
    }

    params = {
        'timeout': timeout,
        'memory': memory,
        'maxItems': max_items,
        'maxTotalChargeUsd': max_total_charge_usd,
        'format': format,
        'clean': int(clean),
        'offset': offset,
        'limit': limit,
        'fields': fields,
        'omit': omit
    }

    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}

    request_url = f"{url}/{actorId}/run-sync-get-dataset-items"
    response = requests.post(request_url, headers=headers, json=input_payload, params=params)

    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to run actor and get dataset items: {response.status_code} - {response.text}")

