import time
import os
import shutil
import requests
from playwright.sync_api import sync_playwright

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
jenkins_ip = "3.6.90.59"
tfstate_file = ROOT / "terraform" / "terraform.tfstate"
if tfstate_file.exists():
    try:
        with open(tfstate_file, "r", encoding="utf-8") as f:
            tf = json.load(f)
            if "outputs" in tf and "jenkins_public_ip" in tf["outputs"]:
                jenkins_ip = tf["outputs"]["jenkins_public_ip"]["value"]
    except Exception:
        pass

JENKINS_URL = os.getenv("JENKINS_URL", f"http://{jenkins_ip}:8080")
LOGIN_URL = f"{JENKINS_URL}/login"
USERNAME = "admin"
PASSWORD = "CHANGE_ME"

SCREENSHOT_DEST = os.path.abspath("screenshots/screenshot_jenkins.png")
BRAIN_DEST = r"C:\Users\savin\.gemini\antigravity\brain\614c16a7-8f71-4cbb-bcf7-79712286a07b\screenshot_jenkins.png"

def wait_for_jenkins(timeout_sec=120):
    print(f"Waiting for Jenkins at {LOGIN_URL}...")
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            r = requests.get(LOGIN_URL, timeout=4)
            if r.status_code == 200 and "Jenkins" in r.text:
                print(f"Jenkins is UP! (status {r.status_code})")
                return True
        except Exception:
            pass
        time.sleep(3)
    raise TimeoutError(f"Jenkins did not become ready within {timeout_sec}s.")

def capture_dashboard():
    wait_for_jenkins()
    time.sleep(5) # give Jenkins an extra moment to settle JCasC jobs

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox"]
        )
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print("Navigating to login page...")
        page.goto(LOGIN_URL, wait_until="networkidle")

        print("Filling login credentials...")
        page.locator("input[name='j_username'], #j_username").fill(USERNAME)
        page.locator("input[name='j_password']").fill(PASSWORD)
        
        print("Submitting login form...")
        page.locator("button[name='Submit'], button[type='submit'], .jenkins-button--primary").click()
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        print(f"Logged in! Current URL: {page.url}")

        # Check if CloudNotes-Pipeline job exists
        job_url = f"{JENKINS_URL}/job/CloudNotes-Pipeline/"
        print(f"Checking pipeline job URL: {job_url}...")
        try:
            r = page.goto(job_url, wait_until="networkidle", timeout=10000)
            if r and r.status == 200:
                print("Pipeline job page loaded successfully.")
                time.sleep(2)
            else:
                print(f"Job URL status {r.status if r else 'unknown'}, returning to main dashboard...")
                page.goto(f"{JENKINS_URL}/", wait_until="networkidle")
        except Exception as e:
            print(f"Could not load specific job page ({e}), falling back to main dashboard.")
            page.goto(f"{JENKINS_URL}/", wait_until="networkidle")

        time.sleep(2)

        # Save screenshot
        os.makedirs(os.path.dirname(SCREENSHOT_DEST), exist_ok=True)
        page.screenshot(path=SCREENSHOT_DEST, full_page=False)
        print(f"Saved authenticated Jenkins screenshot to {SCREENSHOT_DEST}")

        if os.path.exists(os.path.dirname(BRAIN_DEST)):
            shutil.copy2(SCREENSHOT_DEST, BRAIN_DEST)
            print(f"Copied screenshot to brain artifact directory: {BRAIN_DEST}")

        browser.close()

if __name__ == "__main__":
    capture_dashboard()
