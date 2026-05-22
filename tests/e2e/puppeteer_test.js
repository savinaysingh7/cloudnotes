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

  await takeShot('goal_local_app.png', 'http://localhost:80');
  await takeShot('goal_aws_app.png', 'http://3.235.124.255/');

  console.log('Screenshot Grafana...');
  try {
      await page.goto('http://localhost:3001/login', { waitUntil: 'networkidle2', timeout: 10000 });
      const userInputs = await page.$$('input[name="user"]');
      if(userInputs.length > 0) {
          await userInputs[0].type('admin');
          const passInputs = await page.$$('input[name="password"]');
          if(passInputs.length > 0) await passInputs[0].type('admin');
          const loginBtn = await page.evaluateHandle(() => Array.from(document.querySelectorAll('button')).find(el => (el.textContent || '').toLowerCase().includes('log in')));
          if(loginBtn) await loginBtn.evaluate(b => b?.click());
          await new Promise(r => setTimeout(r, 3000));
      }
  } catch(e) {}
  await takeShot('goal_grafana.png', 'http://localhost:3001/dashboards');

  await takeShot('goal_prometheus.png', 'http://localhost:9091/alerts');
  await takeShot('goal_jenkins.png', 'http://3.234.255.197:8080/job/CloudNotes-Pipeline/');

  console.log('Tests completed.');
  await browser.close();
})();
