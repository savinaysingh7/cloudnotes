import urllib.request
import time
import concurrent.futures

import os
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
app_ip = "3.108.191.94"
tfstate_file = ROOT / "terraform" / "terraform.tfstate"
if tfstate_file.exists():
    try:
        with open(tfstate_file, "r", encoding="utf-8") as f:
            tf = json.load(f)
            if "outputs" in tf and "app_public_ip" in tf["outputs"]:
                app_ip = tf["outputs"]["app_public_ip"]["value"]
    except Exception:
        pass

app_host = sys.argv[1] if len(sys.argv) > 1 else os.getenv("APP_IP", app_ip)
TARGET_URL = f"http://{app_host}/api/notes"

def fetch(i):
    try:
        req = urllib.request.Request(TARGET_URL, headers={"User-Agent": "TrafficTest/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status
    except Exception as e:
        return str(e)

def main():
    print(f"Sending synthetic traffic to {TARGET_URL}...")
    start_time = time.time()
    total_reqs = 300
    workers = 15
    success = 0
    errors = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fetch, i) for i in range(total_reqs)]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res == 200:
                success += 1
            else:
                errors += 1

    elapsed = time.time() - start_time
    print(f"Completed {total_reqs} requests in {elapsed:.2f}s ({total_reqs/elapsed:.1f} req/s). Success: {success}, Errors: {errors}")

if __name__ == '__main__':
    main()
