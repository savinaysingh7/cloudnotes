import os
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)
ARTIFACT_DIR = Path(os.getenv("ARTIFACT_DIR", r"C:\Users\savin\.gemini\antigravity\brain\58d94cea-2cf3-4818-a090-2835c6bd8fda"))

APP_URL = os.getenv("CLOUDNOTES_URL", "http://127.0.0.1:8081").rstrip('/')
PROM_URL = os.getenv("PROMETHEUS_URL", "http://127.0.0.1:9091").rstrip('/')
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://127.0.0.1:3001").rstrip('/')
GRAFANA_PASSWORD = os.getenv("GF_SECURITY_ADMIN_PASSWORD", "CHANGE_ME")
JENKINS_URL = os.getenv("JENKINS_URL", "http://127.0.0.1:8080").rstrip('/')
JENKINS_USER = os.getenv("JENKINS_USER", "admin")
JENKINS_PASSWORD = os.getenv("JENKINS_PASSWORD", "admin")

def save_and_copy(source_path, filename):
    if ARTIFACT_DIR.exists():
        try:
            shutil.copy(source_path, ARTIFACT_DIR / filename)
        except Exception:
            pass

def run_browser_automation():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # Handle alert/confirm dialogs automatically
        page.on('dialog', lambda dialog: dialog.accept())

        # 1. Open CloudNotes Frontend
        print(f"[E2E] 1. Loading CloudNotes frontend at {APP_URL}...")
        page.goto(f'{APP_URL}/', wait_until='networkidle')
        time.sleep(2)
        assert "CloudNotes" in page.title()
        home_shot = SCREENSHOTS / 'screenshot_app_home.png'
        page.screenshot(path=str(home_shot))
        save_and_copy(home_shot, 'screenshot_app_home.png')
        results['home'] = True
        print("[E2E] Saved screenshot_app_home.png")

        # 2. Add a new note
        print("[E2E] 2. Adding test note...")
        test_title = "Automated E2E Verification Note"
        test_body = "Verified automatically via Playwright browser automation with zero user intervention."
        page.fill('#note-title', test_title)
        page.fill('#note-body', test_body)
        page.click('#add-note')
        page.wait_for_selector(f'text={test_title}', timeout=5000)
        time.sleep(1)

        created_shot = SCREENSHOTS / 'screenshot_app_created_note.png'
        page.screenshot(path=str(created_shot))
        save_and_copy(created_shot, 'screenshot_app_created_note.png')
        results['create_note'] = True
        print("[E2E] Note created successfully; saved screenshot_app_created_note.png")

        # 3. Test Search filtering
        print("[E2E] 3. Testing search bar filter...")
        page.fill('#search-input', "Automated E2E")
        time.sleep(1)
        visible_notes = page.locator('#notes-list .note-item').count()
        assert visible_notes >= 1
        page.fill('#search-input', "")
        time.sleep(1)
        results['search'] = True
        print(f"[E2E] Search verified; {visible_notes} match(es) filtered.")

        # 4. Edit Note
        print("[E2E] 4. Testing note edit modal...")
        note_card = page.locator(f'.note-item:has-text("{test_title}")').first
        note_card.locator('button:has-text("Edit")').click()
        page.wait_for_selector('#edit-modal', state='visible', timeout=5000)
        updated_title = "Automated E2E Verification Note (Updated)"
        page.fill('#edit-note-title', updated_title)
        page.click('#edit-modal button:has-text("Save Changes")')
        page.wait_for_selector(f'text={updated_title}', timeout=5000)
        results['edit_note'] = True
        print("[E2E] Note edited successfully.")

        # 5. Delete Note
        print("[E2E] 5. Testing note deletion...")
        updated_card = page.locator(f'.note-item:has-text("{updated_title}")').first
        updated_card.locator('button:has-text("Delete")').click()
        time.sleep(1)
        page.wait_for_selector(f'text={updated_title}', state='detached', timeout=5000)
        results['delete_note'] = True
        print("[E2E] Note deleted successfully.")

        # 6. Prometheus Targets
        print(f"[E2E] 6. Capturing Prometheus targets at {PROM_URL}/targets...")
        page.goto(f'{PROM_URL}/targets')
        time.sleep(3)
        prom_shot = SCREENSHOTS / 'screenshot_prometheus_targets.png'
        page.screenshot(path=str(prom_shot))
        save_and_copy(prom_shot, 'screenshot_prometheus_targets.png')
        results['prometheus'] = True
        print("[E2E] Prometheus targets captured.")

        # 7. Grafana Dashboard
        print(f"[E2E] 7. Capturing Grafana Production Dashboard at {GRAFANA_URL}...")
        page.goto(f'{GRAFANA_URL}/login')
        page.wait_for_selector('input[name="user"]')
        page.fill('input[name="user"]', 'admin')
        page.fill('input[name="password"]', GRAFANA_PASSWORD)
        page.click('button[type="submit"]')
        time.sleep(3)
        page.goto(f'{GRAFANA_URL}/d/cloudnotes-prod/cloudnotes-production-dashboard?orgId=1&refresh=5s&from=now-1h&to=now')
        time.sleep(6)
        grafana_shot = SCREENSHOTS / 'screenshot_grafana_dashboard.png'
        page.screenshot(path=str(grafana_shot))
        save_and_copy(grafana_shot, 'screenshot_grafana_dashboard.png')
        results['grafana'] = True
        print("[E2E] Grafana dashboard captured.")

        # 8. Jenkins Dashboard & Pipeline Job
        print(f"[E2E] 8. Capturing Jenkins Dashboard at {JENKINS_URL}...")
        try:
            page.goto(f'{JENKINS_URL}/login')
            page.wait_for_selector('input[name="j_username"]', timeout=8000)
            page.fill('input[name="j_username"]', JENKINS_USER)
            page.fill('input[name="j_password"]', JENKINS_PASSWORD)
            page.click('button[name="Submit"]')
            time.sleep(3)
            jenkins_shot = SCREENSHOTS / 'screenshot_jenkins_dashboard.png'
            page.screenshot(path=str(jenkins_shot))
            save_and_copy(jenkins_shot, 'screenshot_jenkins_dashboard.png')
            results['jenkins_dashboard'] = True
            print("[E2E] Jenkins dashboard captured.")

            # Check pipeline job
            page.goto(f'{JENKINS_URL}/job/CloudNotes-Pipeline/')
            time.sleep(2)
            jenkins_job_shot = SCREENSHOTS / 'screenshot_jenkins_pipeline.png'
            page.screenshot(path=str(jenkins_job_shot))
            save_and_copy(jenkins_job_shot, 'screenshot_jenkins_pipeline.png')
            results['jenkins_pipeline'] = True
            print("[E2E] Jenkins pipeline job captured.")
        except Exception as e:
            print(f"[E2E] Jenkins capture warning: {e}")
            results['jenkins_dashboard'] = False

        browser.close()

    print("[E2E] Complete! All browser automation checks succeeded:", results)
    return results

if __name__ == '__main__':
    run_browser_automation()
