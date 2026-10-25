// Shared set-up for the browser tests: launches Chromium through Playwright, opens the game file, collects page errors
// and native dialogs, and counts checks. Run a suite with `node touchline/tests/<name>.test.js`; it ends with ALL PASS
// or the number that failed, and exits non-zero on failure.
const path = require('path');
const { chromium } = require('playwright');
const GAME = 'file://' + path.resolve(__dirname, '..', 'index.html');
let failures = 0;
function check(label, ok, extra = '') { if (!ok) failures++; console.log((ok ? 'PASS ' : 'FAIL ') + label + (extra ? ' :: ' + extra : '')) }
async function launch() { return chromium.launch({ args: ['--no-sandbox'] }) }
async function open(browser, opts = {}) {
  const page = await browser.newPage({ viewport: opts.viewport || { width: 1440, height: 900 }, isMobile: !!opts.mobile, hasTouch: !!opts.mobile });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()) });
  page.on('dialog', d => { errors.push('native dialog: ' + d.message()); d.dismiss() });
  page.on('request', r => { if (!/^(file|data|blob):/.test(r.url())) errors.push('network request: ' + r.url()) });
  await page.goto(GAME);
  return { page, errors };
}
// A club career a few rounds in, with big moments and in-game decisions off so nothing waits for a tap.
const CLUB = (team = 'Munster', league = 'urc', rounds = 3) => page => page.evaluate(([team, league, rounds]) => { queueMoment = () => {}; callModeOf = () => 'off'; setupLeague = league; newCareer('club', team); for (let i = 0; i < rounds; i++) { while (!nextUserFixture()) advance({ quiet: true }); advance({ quiet: true }); closeModal() } switchTab('Overview'); render() }, [team, league, rounds]);
// Runs the live clock without its timer, answering decisions as the assistant would; stops at an injury card for you.
const RUN_LIVE = to => { const M = live.M; for (let i = 0; i < 400 && !M.done && M.min < to; i++) { if (M.call) { if (M.call.type === 'inj') break; M.cur = []; resolveCall(M, callRec(M)); for (const e of M.cur) liveEmit(e) } if (M.htPending) { M.cur = []; applyHalfTime(M, 'calm', false); M.htPending = false; for (const e of M.cur) liveEmit(e) } for (const e of matchMinute(M)) liveEmit(e); if (M.call && M.call.type === 'inj') break } live.min = M.min; liveRefresh(); const m = document.getElementById('live-moment'); if (m) m.hidden = true; return M.min };
function done(browser) { console.log(failures ? `--- ${failures} FAILED ---` : 'ALL PASS'); return browser.close().then(() => process.exit(failures ? 1 : 0)) }
module.exports = { launch, open, check, done, CLUB, RUN_LIVE, GAME };
