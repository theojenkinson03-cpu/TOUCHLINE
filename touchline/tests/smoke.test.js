// Every career type, every page, on a computer and a phone: no errors, nothing crashes to the "could not be displayed"
// card, nothing scrolls sideways. Then a live match to full time and a club season played to the end and rolled over.
const { launch, open, check, done, RUN_LIVE } = require('./harness');
const CAREERS = [
  ['Super Rugby club', () => { setupLeague = 'super'; newCareer('club', 'Blues') }],
  ['URC club', () => { setupLeague = 'urc'; newCareer('club', 'Leinster') }],
  ['Premiership club', () => { setupLeague = 'prem'; newCareer('club', 'Bath') }],
  ['Top 14 club', () => { setupLeague = 'top14'; newCareer('club', 'Toulouse') }],
  ['World Cup', () => { newCareer('international', 'Wales') }],
  ['International manager', () => { newCareer('intlcareer', 'Scotland') }],
  ['Club World Cup', () => { newCareer('clubworldcup', 'Leinster') }],
  ['Coaching career', () => { heroNameDraft = 'Test Coach'; newCareer('hero', 'Munster') }],
  ['Player career', () => { proDraft = { ...proDraft, name: 'Test Player', club: 'Leinster' }; newCareer('pro') }]
];
(async () => {
  const browser = await launch();
  for (const [vp, mobile] of [[{ width: 1440, height: 900 }, false], [{ width: 390, height: 844 }, true]]) {
    const { page, errors } = await open(browser, { viewport: vp, mobile });
    for (const [name, make] of CAREERS) {
      const started = await page.evaluate(src => { queueMoment = () => {}; callModeOf = () => 'off'; try { (0, eval)('(' + src + ')')() } catch (e) { return 'start: ' + e.message } const g = game(); if (!g) return 'no career'; screen = 'career'; for (let i = 0; i < 3; i++) { try { if (g.mode === 'international' && g.phase === 'Selection') break; advance({ quiet: true }) } catch (e) { return 'advance: ' + e.message } closeModal() } return 'ok' }, make.toString());
      const bad = await page.evaluate(() => { const g = game(), out = []; if (!g) return ['no career']; for (const t of tabsFor(g)) { switchTab(t); render(); const txt = document.querySelector('#app').textContent; if (/This screen could not be displayed/.test(txt)) out.push(t + ': crashed'); const over = document.documentElement.scrollWidth - innerWidth; if (over > 0) out.push(t + ': ' + over + 'px wider') } return out });
      check(`${vp.width}px · ${name}: starts, and every page draws without errors or sideways scroll`, started === 'ok' && !bad.length && !errors.length, JSON.stringify({ started, bad, errors: errors.slice(0, 2) }));
      errors.length = 0;
    }
    await page.close();
  }

  // A live match to full time: kick-off, half-time, a change by you, Skip to full time, the report
  const { page, errors } = await open(browser);
  await page.evaluate(() => { queueMoment = () => {}; callModeOf = () => 'off'; setupLeague = 'urc'; newCareer('club', 'Munster'); matchCentreOn = () => true; game().quickMatch = false; switchTab('Overview'); render(); prematch() });
  await page.click('button[data-act="kickoff"]'); await page.click('button[data-act="live-pause"]');
  // An injury stops the clock for your choice: pick the first replacement offered, as a manager would, and carry on
  for (let i = 0; i < 4; i++) { const m = await page.evaluate(RUN_LIVE, 52); const inj = await page.evaluate(() => { const M = live.M, C = M.call; if (!C || C.type !== 'inj') return false; M.cur = []; resolveCall(M, C.opts[0]); for (const e of M.cur) liveEmit(e); M.cur = []; liveRefresh(); return true }); if (!inj || m >= 52) break }
  const sub = await page.evaluate(() => { if (live.M.call) return 'call'; const b = document.querySelector('#live-pane [data-act="live-sub-pick"]'); if (!b) return 'none'; b.click(); document.querySelector('#live-pane .lu-cand').click(); return Object.values(live.M.t[live.M.user].onAt).some(m => m > 0) ? 'made' : 'not made' });
  await page.click('button[data-act="live-skip"]'); await page.waitForTimeout(300);
  await page.click('button[data-act="live-done"]').catch(() => {}); await page.waitForTimeout(300);
  const ft = await page.evaluate(() => ({ live: !!live, report: !!document.querySelector('#modal[open]'), played: game().results.some(r => r.a === game().team || r.b === game().team) }));
  check('a live match: a change by you, Skip to full time, and the report', sub === 'made' && !ft.live && ft.report && ft.played && !errors.length, JSON.stringify({ sub, ft, errors: errors.slice(0, 2) }));

  // A whole club season, the finals and the rollover into the next (past the confirmation about expiring contracts)
  const season = await page.evaluate(() => { closeModal(); const s = game(), y = s.year; let g = 0; while (s.year === y && g++ < 60) { if (s.phase === 'Complete') { beginNextSeason(); break } advance({ quiet: true }); closeModal() } return { year: game().year, was: y, phase: game().phase, round: game().round } });
  check('a club season plays to the end and rolls over into the next', season.year === season.was + 1 && !errors.length, JSON.stringify({ season, errors: errors.slice(0, 2) }));
  await done(browser);
})();
