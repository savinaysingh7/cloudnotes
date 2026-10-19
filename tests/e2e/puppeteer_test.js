const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-web-security'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  const takeShot = async (name, url) => {
      console.log(`Screenshot ${name}...`);
      try {
          await page.goto(url, { waitUntil: 'networkidle2', timeout: 15000 });
      } catch(e) {
          console.log(`Goto error: ${e.message}, taking screenshot anyway...`);
      }
      await new Promise(r => setTimeout(r, 2000));
      await page.screenshot({ path: path.join(__dirname, name) });
  };

  const localAppUrl = process.env.LOCAL_APP_URL || 'http://localhost:80';
  const awsAppUrl = process.env.AWS_APP_URL || (process.env.APP_IP ? `http://${process.env.APP_IP}/` : 'http://localhost:80');
  const jenkinsUrl = process.env.JENKINS_URL || (process.env.JENKINS_IP ? `http://${process.env.JENKINS_IP}:8080/job/CloudNotes-Pipeline/` : 'http://localhost:8080/job/CloudNotes-Pipeline/');
  const grafanaUrl = process.env.GRAFANA_URL || 'http://localhost:3001';
  const promUrl = process.env.PROMETHEUS_URL || 'http://localhost:9091';

  await takeShot('goal_local_app.png', localAppUrl);
  await takeShot('goal_aws_app.png', awsAppUrl);

  console.log('Screenshot Grafana...');
  try {
      await page.goto(`${grafanaUrl}/login`, { waitUntil: 'networkidle2', timeout: 10000 });
      const userInputs = await page.$$('input[name="user"]');
      if(userInputs.length > 0) {
          await userInputs[0].type('admin');
          const passInputs = await page.$$('input[name="password"]');
          if(passInputs.length > 0) await passInputs[0].type(process.env.GF_SECURITY_ADMIN_PASSWORD || 'CHANGE_ME');
          const loginBtn = await page.evaluateHandle(() => Array.from(document.querySelectorAll('button')).find(el => (el.textContent || '').toLowerCase().includes('log in')));
          if(loginBtn) await loginBtn.evaluate(b => b?.click());
          await new Promise(r => setTimeout(r, 3000));
      }
  } catch(e) {}
  await takeShot('goal_grafana.png', `${grafanaUrl}/dashboards`);

  await takeShot('goal_prometheus.png', `${promUrl}/alerts`);
  await takeShot('goal_jenkins.png', jenkinsUrl);

  console.log('Tests completed.');
  await browser.close();
})();
