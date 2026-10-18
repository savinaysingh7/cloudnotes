import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
SCREENSHOTS.mkdir(exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\savin\.gemini\antigravity\brain\ea0170fa-9f34-4ce4-b9b9-972a62b9f5a1")

def run_browser_automation():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # Handle alert/confirm dialogs automatically
        page.on('dialog', lambda dialog: dialog.accept())

        # 1. Open CloudNotes Frontend
        print("[E2E] 1. Loading CloudNotes frontend at http://127.0.0.1:8081...")
        page.goto('http://127.0.0.1:8081/', wait_until='networkidle')
        time.sleep(2)
        assert "CloudNotes" in page.title()
        home_shot = SCREENSHOTS / 'screenshot_app_home.png'
        page.screenshot(path=str(home_shot))
        shutil.copy(home_shot, ARTIFACT_DIR / 'screenshot_app_home.png')
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
        shutil.copy(created_shot, ARTIFACT_DIR / 'screenshot_app_created_note.png')
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
        print("[E2E] 6. Capturing Prometheus targets...")
        page.goto('http://127.0.0.1:9091/targets')
        time.sleep(3)
        prom_shot = SCREENSHOTS / 'screenshot_prometheus_targets.png'
        page.screenshot(path=str(prom_shot))
        shutil.copy(prom_shot, ARTIFACT_DIR / 'screenshot_prometheus_targets.png')
        results['prometheus'] = True
        print("[E2E] Prometheus targets captured.")

        # 7. Grafana Dashboard
        print("[E2E] 7. Capturing Grafana Production Dashboard...")
        page.goto('http://127.0.0.1:3001/login')
        page.wait_for_selector('input[name="user"]')
        page.fill('input[name="user"]', 'admin')
        page.fill('input[name="password"]', 'CHANGE_ME')
        page.click('button[type="submit"]')
        time.sleep(3)
        page.goto('http://127.0.0.1:3001/d/cloudnotes-prod/cloudnotes-production-dashboard?orgId=1&refresh=5s&from=now-1h&to=now')
        time.sleep(6)
        grafana_shot = SCREENSHOTS / 'screenshot_grafana_dashboard.png'
        page.screenshot(path=str(grafana_shot))
        shutil.copy(grafana_shot, ARTIFACT_DIR / 'screenshot_grafana_dashboard.png')
        results['grafana'] = True
        print("[E2E] Grafana dashboard captured.")

        browser.close()

    print("[E2E] Complete! All browser automation checks succeeded:", results)
    return results

if __name__ == '__main__':
    run_browser_automation()
