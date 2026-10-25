// Skill, form and fitness out of 100, each a ring with its number: the squad list, form everywhere, the match centre's
// line-up (form moving with his play) and the phone layouts.
const { launch, open, check, done, CLUB, RUN_LIVE } = require('./harness');
(async () => {
  const browser = await launch();
  const { page, errors } = await open(browser);
  await CLUB()(page);

  // 1. Form out of 100 is the star scale on a continuous dial
  const scale = await page.evaluate(() => ({ lo: formPct(-7), mid: formPct(0), hi: formPct(3.7), top: formPct(7), stars: [-5, -2.6, -.5, 1.6, 3.7].map(f => [formStars({ form: f }), formPct(f)]), mono: Array.from({ length: 141 }, (_, i) => formPct(-7 + i / 10)).every((v, i, a) => i === 0 || v >= a[i - 1]) }));
  check('form out of 100: 0 at the bottom, about 65 when neutral, 100 at five stars, and never falling as form rises', scale.lo === 0 && scale.mid === 65 && scale.hi === 100 && scale.top === 100 && scale.mono && scale.stars.every(([st, v]) => Math.abs(st * 20 - v) <= 10), JSON.stringify(scale));

  // 2. Squad list: Skill, Form and Fitness side by side, each a ring with the right number and colour
  await page.evaluate(() => { switchTab('Squad'); render() });
  const sq = await page.evaluate(() => { const s = game(), heads = [...document.querySelectorAll('#app table.v3-ptable thead th')].map(t => t.textContent), rows = [...document.querySelectorAll('#app table.v3-ptable tbody tr[data-id]')].map(tr => { const p = player(tr.dataset.id), r = c => tr.querySelector(c + ' .st-ring'); return { skill: r('.c-skill')?.textContent === String(overall(p)), skillTier: r('.c-skill')?.classList.contains(ratingTier(overall(p))), form: r('.c-form')?.textContent === String(formPct(p)), fit: r('.c-fit')?.textContent === Math.round(p.fitness) + '%', fitBand: r('.c-fit')?.className.includes(statBand('fit', Math.round(p.fitness))), rings: tr.querySelectorAll('.v3-ring').length } }); return { heads, n: rows.length, bad: rows.filter(r => !(r.skill && r.skillTier && r.form && r.fit && r.fitBand && r.rings === 3)).length, stars: document.querySelectorAll('#app .fstars').length } });
  check('squad list: Skill, Form and Fitness columns, every row three rings with the engine’s numbers', sq.heads.includes('Skill') && sq.heads.includes('Form') && sq.heads.includes('Fitness') && !sq.heads.includes('OVR') && sq.n >= 30 && sq.bad === 0 && sq.stars === 0, JSON.stringify(sq));

  // 3. Form is out of 100 wherever it shows: the player card, the transfer list, the matchday page
  const elsewhere = await page.evaluate(() => { const out = {}, p = pool(game().team)[0]; profile(p.id); out.profile = { ring: !!document.querySelector('#modal .st-form'), val: document.querySelector('#modal .st-form b')?.textContent === String(formPct(p)), stars: document.querySelectorAll('#modal .fstars').length }; closeModal(); for (const t of ['Transfers', 'Matchday', 'Squad report']) { switchTab(t); render(); out[t] = { stars: document.querySelectorAll('#app .fstars').length, rings: document.querySelectorAll('#app .st-form').length } } return out });
  check('form shows as a ring out of 100 on the player card, and no page still draws form stars', elsewhere.profile.ring && elsewhere.profile.val && elsewhere.profile.stars === 0 && ['Transfers', 'Matchday', 'Squad report'].every(t => elsewhere[t].stars === 0), JSON.stringify(elsewhere));

  // 4. Match centre line-up: the same three rings; form starts where it stood and moves with his play
  await page.evaluate(() => { matchCentreOn = () => true; switchTab('Overview'); render(); prematch() });
  await page.click('button[data-act="kickoff"]'); await page.click('button[data-act="live-pause"]');
  const ko = await page.evaluate(() => { const M = live.M, U = M.t[M.user], heads = [...document.querySelectorAll('#live-pane .lu-table thead th')].map(t => t.textContent), rows = [...document.querySelectorAll('#live-pane .lu-table:not(.lu-bench):not(.lu-off) tbody tr[data-id]')]; return { heads, n: rows.length, ok: rows.every(tr => { const p = player(tr.dataset.id); return tr.querySelector('.lu-skill .st-ring')?.textContent === String(overall(p)) && tr.querySelector('.lu-form .st-ring')?.textContent === String(formPct(p)) && tr.querySelector('.lu-fit .st-ring')?.textContent === Math.round(p.fitness) + '%' }) } });
  check('line-up at kick-off: Skill, Form and Fitness rings, form exactly where it stood before the match', ko.heads.slice(3, 6).join() === 'Skill,Form,Fitness' && ko.n === 15 && ko.ok, JSON.stringify(ko));
  await page.evaluate(() => { const U = live.M.t[live.M.user]; for (const id of U.on) if (id) U.inj[id] = 0 });
  await page.evaluate(RUN_LIVE, 50);
  const mv = await page.evaluate(() => { const M = live.M, U = M.t[M.user], id = U.on[11], p = player(id), before = liveForm(M, U, id), r0 = liveRating(M, U, id); engTouch(M, id, 'tries'); engTouch(M, id, 'tries'); const after = liveForm(M, U, id); const c = M.contrib.get(id); c.tries -= 2; const half = (() => { const mins = M.min - U.onAt[id]; return Math.abs((before - p.form) / Math.max(1e-9, ((clamp(p.form * .85 + clamp((r0 - (p.base + p.growth - 75) * .02 - RATING_BASELINE) * 1.5, -3, 3), -7, 7)) - p.form)) - mins / 80) < .02 })(); liveRefresh(); const cell = document.querySelector(`#live-pane tr[data-id="${id}"] .lu-form .st-ring`); return { before, after, half, shown: cell?.textContent === String(formPct(before)), title: /match rating so far \d/.test(cell?.getAttribute('title') || '') } });
  check('line-up form moves with his play in step with his minutes, and two tries lift it', mv.after > mv.before && mv.half && mv.shown && mv.title, JSON.stringify(mv));
  const keep = await page.evaluate(() => { const before = document.querySelector('#live-pane .lu-table tbody tr'); live.M.t[live.M.user].pf[live.M.t[live.M.user].on[0]] += .2; liveRefresh(); return { same: document.querySelector('#live-pane .lu-table tbody tr') === before, fit: document.querySelector('#live-pane .lu-table tbody tr .lu-fit .st-ring').textContent === liveFit(live.M.t[live.M.user], live.M.t[live.M.user].on[0]) + '%' } });
  check('each minute the rings update in place, without redrawing the rows under your finger', keep.same && keep.fit, JSON.stringify(keep));

  // 5. Phones: the squad's Pocket rows label form and skill; nothing is wider than the screen
  const ph = await open(browser, { viewport: { width: 390, height: 844 }, mobile: true });
  await CLUB()(ph.page);
  for (const [w, txt] of [[390, 'std'], [360, 'lg']]) {
    await ph.page.setViewportSize({ width: w, height: 800 }); await ph.page.evaluate(t => { setPref('text', t); switchTab('Squad'); render() }, txt);
    const sp = await ph.page.evaluate(() => { const tr = document.querySelector('#app table.v3-ptable tbody tr[data-id]'), lab = s => getComputedStyle(tr.querySelector(s), s.includes('skill') ? '::after' : '::before').content; return { over: document.documentElement.scrollWidth - innerWidth, skill: lab('.c-skill .st-ring'), form: lab('.c-form .st-ring'), h: Math.round(tr.getBoundingClientRect().height) } });
    check(`phone ${w}px${txt === 'lg' ? ' with large text' : ''}: Pocket rows label Form and Skill, rows stay short, no sideways scroll`, sp.over <= 0 && /Skill/.test(sp.skill) && /Form/.test(sp.form) && sp.h <= 76, JSON.stringify(sp));
  }
  await ph.page.setViewportSize({ width: 390, height: 844 }); await ph.page.evaluate(() => { setPref('text', 'std'); matchCentreOn = () => true; switchTab('Overview'); render(); prematch() });
  await ph.page.click('button[data-act="kickoff"]'); await ph.page.click('button[data-act="live-pause"]'); await ph.page.evaluate(RUN_LIVE, 30);
  const pl = await ph.page.evaluate(() => ({ over: document.documentElement.scrollWidth - innerWidth, wide: [...document.querySelectorAll('#live-pane .lu-table')].some(t => t.getBoundingClientRect().right > innerWidth + 1), rings: document.querySelectorAll('#live-pane .lu-table:not(.lu-bench):not(.lu-off) tbody tr[data-id] .st-ring').length }));
  check('phone line-up: three rings on each of the fifteen rows, nothing wider than the screen', pl.over <= 0 && !pl.wide && pl.rings === 45, JSON.stringify(pl));

  // 6. The guide says so
  const guide = await page.evaluate(() => { closeModal(); try { endLive() } catch (e) {} screen = 'help'; render(); const t = document.querySelector('#app').textContent; screen = 'career'; render(); return { form: /Form<\/b>|Form is separate, shown out of 100/.test(t) || t.includes('Form is separate, shown out of 100'), lineup: t.includes('skill, form and fitness out of 100'), stars: t.includes('one to five stars') } });
  check('the guide describes form, skill and fitness out of 100 and no longer mentions form stars', guide.form && guide.lineup && !guide.stars, JSON.stringify(guide));

  const all = [...errors, ...ph.errors];
  check('no page errors, native dialogs or network requests', !all.length, all.slice(0, 3).join(' | '));
  await done(browser);
})();
