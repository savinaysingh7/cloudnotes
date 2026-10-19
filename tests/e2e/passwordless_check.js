const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const tfstatePath = path.join(__dirname, '..', '..', 'terraform', 'terraform.tfstate');
const tf = JSON.parse(fs.readFileSync(tfstatePath, 'utf8'));
const appIp = tf.outputs.app_public_ip.value;
const jenkinsIp = tf.outputs.jenkins_public_ip.value;

const APP_URL = `http://${appIp}`;
const PROM_URL = `http://${appIp}:9091`;
const GRAFANA_URL = `http://${appIp}:3001`;
const JENKINS_URL = `http://${jenkinsIp}:8080`;

(async () => {
  console.log(`[PASS-CHECK] Testing pure passwordless access on live AWS:`);
  console.log(`  App: ${APP_URL}`);
  console.log(`  Jenkins: ${JENKINS_URL}`);
  console.log(`  Grafana: ${GRAFANA_URL}`);
  console.log(`  Prometheus: ${PROM_URL}`);

  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-web-security',
      '--disable-features=HttpsFirstMode,HttpsFirstBalancedMode,HttpsUpgrades'
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // 1. Jenkins Passwordless
  console.log('\n1. Visiting Jenkins root without login credentials...');
  await page.goto(`${JENKINS_URL}/`, { waitUntil: 'networkidle2', timeout: 20000 });
  const jenkinsUrl = page.url();
  const jenkinsTitle = await page.title();
  const hasLoginForm = await page.$('input[name="j_username"]') !== null;
  console.log(`   URL: ${jenkinsUrl}`);
  console.log(`   Title: ${jenkinsTitle}`);
  console.log(`   Has Login Form: ${hasLoginForm}`);
  if (hasLoginForm || jenkinsUrl.includes('/login')) {
    throw new Error('Jenkins prompted for login! Passwordless direct access failed.');
  }
  console.log('   [SUCCESS] Jenkins loaded directly without login prompt.');

  // 2. Grafana Passwordless
  console.log('\n2. Visiting Grafana root without login credentials...');
  await page.goto(`${GRAFANA_URL}/`, { waitUntil: 'networkidle2', timeout: 20000 });
  const grafanaUrl = page.url();
  const grafanaTitle = await page.title();
  const hasGrafanaLogin = await page.$('input[name="user"]') !== null;
  console.log(`   URL: ${grafanaUrl}`);
  console.log(`   Title: ${grafanaTitle}`);
  console.log(`   Has Login Form: ${hasGrafanaLogin}`);
  if (hasGrafanaLogin || grafanaUrl.includes('/login')) {
    throw new Error('Grafana prompted for login! Passwordless direct access failed.');
  }
  console.log('   [SUCCESS] Grafana loaded directly without login prompt.');

  // 3. Prometheus Passwordless
  console.log('\n3. Visiting Prometheus targets...');
  await page.goto(`${PROM_URL}/targets`, { waitUntil: 'networkidle2', timeout: 20000 });
  const promTitle = await page.title();
  console.log(`   Title: ${promTitle}`);
  console.log('   [SUCCESS] Prometheus targets loaded directly.');

  // 4. CloudNotes App
  console.log('\n4. Visiting CloudNotes App...');
  await page.goto(`${APP_URL}/`, { waitUntil: 'networkidle2', timeout: 20000 });
  const appTitle = await page.title();
  console.log(`   Title: ${appTitle}`);
  console.log('   [SUCCESS] CloudNotes app loaded directly.');

  await browser.close();
  console.log('\n=== ALL PASSWORDLESS DIRECT CHECKS PASSED ===');
})().catch(err => {
  console.error('[ERROR]', err);
  process.exit(1);
});
