from playwright.sync_api import sync_playwright
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # 1. Grafana Login & Dashboard
    print('Navigating to Grafana login...')
    page.goto('http://127.0.0.1:3001/login')
    page.wait_for_selector('input[name="user"]')
    page.fill('input[name="user"]', 'admin')
    page.fill('input[name="password"]', 'CHANGE_ME')
    page.click('button[type="submit"]')
    time.sleep(3)

    print('Navigating to CloudNotes Production Dashboard...')
    page.goto('http://127.0.0.1:3001/d/cloudnotes-prod/cloudnotes-production-dashboard?orgId=1&refresh=5s&from=now-1h&to=now')
    time.sleep(6)
    
    # Hide sidebar or collapse menus if open for clean capture
    page.screenshot(path=str(SCREENSHOTS / 'screenshot_grafana_dashboard.png'))
    print('Saved screenshot_grafana_dashboard.png')

    # 2. Prometheus Alerts
    print('Navigating to Prometheus Alerts...')
    page.goto('http://127.0.0.1:9091/alerts')
    time.sleep(3)
    page.screenshot(path=str(SCREENSHOTS / 'screenshot_prometheus_alerts.png'))
    print('Saved screenshot_prometheus_alerts.png')

    # 3. Prometheus Targets
    print('Navigating to Prometheus Targets...')
    page.goto('http://127.0.0.1:9091/targets')
    time.sleep(3)
    page.screenshot(path=str(SCREENSHOTS / 'screenshot_prometheus_targets.png'))
    print('Saved screenshot_prometheus_targets.png')

    browser.close()

print('All monitoring captures completed successfully!')
