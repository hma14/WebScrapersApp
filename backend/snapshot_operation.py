import time
import requests
import json
import os
from dotenv import load_dotenv, find_dotenv

#load_dotenv(find_dotenv(usecwd=True), override=True)
load_dotenv()



API_KEY = os.getenv("BRIGHTDATA_TOKEN")
DATASET_ID = "gd_m7aof0k82r803d5bjm" #"gd_m7aof0k82r803d5bjm"  #"gd_l7q7dkf244hwjntr0" #"ds_amazon_products"   # example dataset ID
OUTPUT_FILE = "snapshot_data.json"

BASE_URL = "https://api.brightdata.com/datasets/v3"
trigger_url = f"{BASE_URL}/trigger"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def trigger_snapshot():
    """Start a snapshot collection"""
    payload = [{
                "url": "https://chatgpt.com/",
                "prompt": "what are the biggest business trends to watch in the next five years?",
                "web_search": "false",
                "additional_prompt": "",
                }]  # input params for dataset
    
    try:
        response = requests.post(f"{trigger_url}?dataset_id={DATASET_ID}&include_errors=true", 
                                 headers=headers, 
                                 json=payload)
        
        response.raise_for_status()
        print(response.json())
        return response.json()["snapshot_id"]
    except requests.exceptions.HTTPError as err:
        print("HTTP error:", err)
        print("Response:", response.text)

def wait_for_snapshot(snapshot_id, timeout=300):
    """Poll until snapshot is ready or timeout (in seconds)"""
    url = f"{BASE_URL}/progress/{snapshot_id}"
    start = time.time()
    while True:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        status = data["status"]
        if status == "ready":
            print("✅ Snapshot ready!")
            return data
        elif status == "failed":
            raise Exception("Snapshot failed.")
        
        if time.time() - start > timeout:
            raise TimeoutError("Snapshot not ready within timeout.")
        
        print("⏳ Waiting... still running")
        time.sleep(10)  # wait 10s before polling again

def get_snapshot_parts(snapshot_id, fmt="json"):
    """Get delivery parts (download URLs)"""
    url = f"{BASE_URL}/snapshot/{snapshot_id}"
    params = {"format": fmt}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def download_snapshot(snapshot_id, fmt="json"):
    """Download a dataset snapshot and save it to a file"""
    url = f"{BASE_URL}/snapshot/{snapshot_id}"
    params = {"format": fmt}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()

    data = resp.json()   # Bright Data dataset snapshots return a list of records

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved {len(data)} records to {OUTPUT_FILE}")
    return data


def download_parts(parts):
    """Download each snapshot part and merge into one JSON list"""
    all_data = []
    for part in parts:
        print(f"⬇️ Downloading part {part['part_id']} ...")
        res = requests.get(part["url"])
        res.raise_for_status()
        part_data = res.json()
        all_data.extend(part_data)

    # save merged data
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(all_data)} records to {OUTPUT_FILE}")


