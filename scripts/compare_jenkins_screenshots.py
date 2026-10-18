import time
import os
from playwright.sync_api import sync_playwright

JENKINS_URL = "http://localhost:8080"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--disable-gpu", "--no-sandbox"])
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    # Login
    page.goto(f"{JENKINS_URL}/login", wait_until="networkidle")
    page.locator("#j_username").fill("admin")
    page.locator("input[name='j_password']").fill("CHANGE_ME")
    page.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # 1. Main Dashboard
    page.goto(f"{JENKINS_URL}/", wait_until="networkidle")
    time.sleep(2)
    page.screenshot(path="screenshots/screenshot_jenkins_main.png")
    print("Saved screenshots/screenshot_jenkins_main.png")

    # 2. Pipeline Job page
    page.goto(f"{JENKINS_URL}/job/CloudNotes-Pipeline/", wait_until="networkidle")
    time.sleep(2)
    page.screenshot(path="screenshots/screenshot_jenkins_job.png")
    print("Saved screenshots/screenshot_jenkins_job.png")

    browser.close()
