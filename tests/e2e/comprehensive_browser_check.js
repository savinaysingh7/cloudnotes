const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const ARTIFACT_DIR = process.env.ARTIFACT_DIR || 'C:\\Users\\savin\\.gemini\\antigravity\\brain\\58d94cea-2cf3-4818-a090-2835c6bd8fda';
const SCREENSHOT_DIR = path.join(__dirname, '..', '..', 'screenshots');
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

function copyToArtifact(filename) {
  const src = path.join(SCREENSHOT_DIR, filename);
  if (fs.existsSync(src) && fs.existsSync(ARTIFACT_DIR)) {
    try {
      fs.copyFileSync(src, path.join(ARTIFACT_DIR, filename));
      console.log(`[E2E] Copied ${filename} to artifact directory.`);
    } catch (e) {
      console.warn(`[E2E] Could not copy ${filename}: ${e.message}`);
    }
  }
}

(async () => {
  console.log('=== STARTING COMPREHENSIVE BROWSER VERIFICATION ===');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1366, height: 768 });

  // Handle any dialogs (e.g., delete confirmation)
  page.on('dialog', async dialog => {
    console.log(`[E2E Dialog] ${dialog.message()}`);
    await dialog.accept();
  });

  const results = {};

  try {
    // 1. CLOUDNOTES WEB UI
    console.log('\n--- 1. Testing CloudNotes Web Application (http://127.0.0.1:8081) ---');
    await page.goto('http://127.0.0.1:8081/', { waitUntil: 'networkidle2', timeout: 15000 });
    const pageTitle = await page.title();
    console.log(`[E2E] Page title: ${pageTitle}`);
    const homeShot = 'screenshot_app_home.png';
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, homeShot) });
    copyToArtifact(homeShot);
    results.appHome = true;

    // Add a test note
    console.log('[E2E] Creating a new test note...');
    await page.type('#note-title', 'Browser Verified Note - CloudNotes AWS');
    await page.type('#note-body', 'Successfully reverse engineered, rebuilt, and verified live via headless browser automation.');
    await page.click('#add-note');
    await new Promise(r => setTimeout(r, 1500));

    const noteCreatedShot = 'screenshot_app_created_note.png';
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, noteCreatedShot) });
    copyToArtifact(noteCreatedShot);
    results.appCreateNote = true;

    // Search filter test
    console.log('[E2E] Testing search filter...');
    await page.type('#search-input', 'Browser Verified');
    await new Promise(r => setTimeout(r, 1000));
    const searchShot = 'screenshot_app_search.png';
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, searchShot) });
    copyToArtifact(searchShot);
    results.appSearch = true;

    // Clear search
    await page.evaluate(() => {
      const input = document.getElementById('search-input');
      input.value = '';
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });
    await new Promise(r => setTimeout(r, 1000));

    // 2. PROMETHEUS METRICS & TARGETS
    console.log('\n--- 2. Testing Prometheus (http://127.0.0.1:9091) ---');
    await page.goto('http://127.0.0.1:9091/targets', { waitUntil: 'networkidle2', timeout: 15000 });
    await new Promise(r => setTimeout(r, 2000));
    const promTargetsShot = 'screenshot_prometheus_targets.png';
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, promTargetsShot) });
    copyToArtifact(promTargetsShot);
    results.prometheusTargets = true;

    // 3. GRAFANA PRODUCTION DASHBOARD
    console.log('\n--- 3. Testing Grafana Monitoring Dashboard (http://127.0.0.1:3001) ---');
    await page.goto('http://127.0.0.1:3001/login', { waitUntil: 'networkidle2', timeout: 15000 });
    const userField = await page.$('input[name="user"]');
    if (userField) {
      await page.type('input[name="user"]', 'admin');
      await page.type('input[name="password"]', process.env.GF_SECURITY_ADMIN_PASSWORD || 'CHANGE_ME');
      const submitBtn = await page.$('button[type="submit"]');
      if (submitBtn) await submitBtn.click();
      await new Promise(r => setTimeout(r, 3000));
    }
    // Navigate to CloudNotes Production Dashboard
    await page.goto('http://127.0.0.1:3001/d/cloudnotes-prod/cloudnotes-production-dashboard?orgId=1&refresh=5s&from=now-1h&to=now', {
      waitUntil: 'networkidle2',
      timeout: 15000
    });
    await new Promise(r => setTimeout(r, 4000));
    const grafanaShot = 'screenshot_grafana_dashboard.png';
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, grafanaShot) });
    copyToArtifact(grafanaShot);
    results.grafanaDashboard = true;

    // 4. JENKINS CI/CD SERVER
    console.log('\n--- 4. Testing Jenkins CI/CD (http://127.0.0.1:8080) ---');
    await page.goto('http://127.0.0.1:8080/login', { waitUntil: 'networkidle2', timeout: 15000 });
    const jenkinsUser = await page.$('input[name="j_username"]');
    if (jenkinsUser) {
      await page.type('input[name="j_username"]', 'admin');
      await page.type('input[name="j_password"]', 'admin');
      const jenkinsSubmit = await page.$('button[name="Submit"]');
      if (jenkinsSubmit) await jenkinsSubmit.click();
      await new Promise(r => setTimeout(r, 3000));
    }

    const jenkinsHomeShot = 'screenshot_jenkins_dashboard.png';
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, jenkinsHomeShot) });
    copyToArtifact(jenkinsHomeShot);
    results.jenkinsDashboard = true;

    // Navigate to CloudNotes-Pipeline job
    console.log('[E2E] Checking CloudNotes-Pipeline job...');
    await page.goto('http://127.0.0.1:8080/job/CloudNotes-Pipeline/', { waitUntil: 'networkidle2', timeout: 15000 });
    await new Promise(r => setTimeout(r, 2000));
    const jenkinsJobShot = 'screenshot_jenkins_pipeline.png';
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, jenkinsJobShot) });
    copyToArtifact(jenkinsJobShot);
    results.jenkinsPipeline = true;

  } catch (err) {
    console.error(`[E2E ERROR] Encountered error during verification: ${err.message}`);
    results.error = err.message;
  } finally {
    await browser.close();
  }

  console.log('\n=== COMPREHENSIVE BROWSER VERIFICATION SUMMARY ===');
  console.log(JSON.stringify(results, null, 2));
})();
