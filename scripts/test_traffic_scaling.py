import urllib.request
import time
import concurrent.futures

TARGET_URL = "http://3.108.191.94/api/notes"

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
