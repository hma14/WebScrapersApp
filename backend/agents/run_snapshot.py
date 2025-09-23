import time
import json
import requests
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()

BASE_URL = "https://api.brightdata.com/datasets/v3"
API_TOKEN = os.getenv("BRIGHTDATA_TOKEN")


headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

def trigger_snapshot(url, location, dataset_id, check_in, check_out, country, currency, adults=2, rooms=1, 
                     web_search="false", additional_prompt=""):
    """Start a new snapshot run"""
    payload = [
        {
            "url": url,
            "location": location,
            "check_in": check_in,
            "check_out": check_out,
            "adults": adults,
            "rooms": rooms,           
            "country": country,
            "currency": currency,
            #"web_search": web_search,          # must be string "true"/"false" for this dataset type
            #"additional_prompt": additional_prompt,
        }
    ]

    resp = requests.post(
        f"{BASE_URL}/trigger?dataset_id={dataset_id}&include_errors=true&type=discover_new&discover_by=search_input",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    snapshot_id = data["snapshot_id"]
    print(f"📸 Triggered snapshot: {snapshot_id}")
    return snapshot_id

def trigger_snapshot_chatgpt(url, prompt, dataset_id, web_search="false", additional_prompt=""):
    """Start a new snapshot run"""
    payload = [
        {
            "url": url,
            "prompt": prompt,
            "web_search": web_search,          # must be string "true"/"false" for this dataset type
            "additional_prompt": additional_prompt,
        }
    ]

    resp = requests.post(
        f"{BASE_URL}/trigger?dataset_id={dataset_id}&include_errors=true",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    snapshot_id = data["snapshot_id"]
    print(f"📸 Triggered snapshot: {snapshot_id}")
    return snapshot_id

async def wait_for_snapshot(snapshot_id, timeout=300):
    """Poll progress until snapshot is ready"""
    url = f"{BASE_URL}/progress/{snapshot_id}"
    start = time.time()
    while True:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        print(f"⏳ Snapshot status: {status}")

        if status == "ready":
            return True
        if status == "failed":
            raise RuntimeError(f"Snapshot failed: {data}")
        if time.time() - start > timeout:
            raise TimeoutError("Snapshot polling timed out")

        time.sleep(5)

def download_snapshot(snapshot_id, output_file="snapshot_results.json", fmt="json"):
    """Download snapshot results and save"""
    url = f"{BASE_URL}/snapshot/{snapshot_id}"
    params = {"format": fmt}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()

    data = resp.json()   # dataset snapshots return a list
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved {len(data)} records to {output_file}")
    return data

async def run_snapshot_booking(url, location, dataset_id, check_in, check_out, country, currency="USD", output_file="snapshot_results.json"):
    """Full pipeline: trigger → wait → download"""
    snapshot_id = trigger_snapshot(url, location, dataset_id, check_in, check_out, 
                                    country, currency, 
                                    web_search="false", additional_prompt="")
    await wait_for_snapshot(snapshot_id)
    results = download_snapshot(snapshot_id, output_file=output_file)
    return results

async def run_snapshot_chatgpt(url, prompt, dataset_id, output_file="snapshot_result_chatgpt"):
    """Full pipeline: trigger → wait → download"""
    snapshot_id = trigger_snapshot_chatgpt(url, prompt, dataset_id, web_search="false", additional_prompt="")
    await wait_for_snapshot(snapshot_id)
    results = download_snapshot(snapshot_id, output_file=output_file)
    return results
