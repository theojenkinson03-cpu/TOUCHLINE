// Headless smoke test: plays full NRL and Super League seasons, a World Cup and an international year in web/index.html.
// Usage: node tools/smoke.js   (needs Playwright with Chromium)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + path.resolve(__dirname, '..', 'web', 'index.html'));
  const out = await page.evaluate(() => {
    const season = team => { newCareer('club', team); const s = game(); let g = 0; while (s.phase !== 'Complete' && g++ < 80) advance({ quiet: true }); return `${team}: ${s.phase}, champions ${s.champion}`; };
    const lines = [season('Penrith Panthers'), season('Wigan Warriors')];
    newCareer('international', 'England'); const w = game(); w.selected = choose33('England'); submitSquad();
    let g = 0; while (w.phase !== 'Complete' && g++ < 20) advance({ quiet: true });
    lines.push(`World Cup: ${w.phase}, champions ${w.champion}`);
    newCareer('intlcareer', 'Tonga'); const t = game();
    for (g = 0; g < 60 && t.phase !== 'Complete'; g++) { if (t.phase === 'Selection') { t.selected = choose33('Tonga'); submitSquad(); continue } if (t.phase === 'League' && !nextUserFixture() && !userFixtureAhead(t)) { simWindow(); continue } advance({ quiet: true }) }
    lines.push(`International year: ${t.phase}`);
    return lines;
  });
  console.log(out.join('\n'));
  if (errors.length) { console.error(errors.join('\n')); process.exitCode = 1 }
  await browser.close();
})();
