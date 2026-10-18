# 6 Again

A rugby league manager, built from Touchline. The same careers, transfer market, staff, inbox, live match centre and
player career, rebuilt around thirteen-a-side and the six-tackle set.

- **NRL** (17 clubs, a bye every round, top-eight finals: qualifying and elimination finals, semis, prelims and a
  Grand Final) and **Super League** (14 clubs, top-six play-offs: eliminators, semis and a Grand Final).
- **State of Origin**: three games through the NRL season. Selected players miss that NRL round for their club.
- **Rugby League World Cup 2026** in its real format: Group A, plus Groups B and C playing each other on one
  combined table, then semi-finals and a final.
- **International career**: mid-season Tests, the Pacific Championships, the Pacific Bowl, the European Championship,
  the Ashes every four years and a World Cup every four.
- **Hero career**, **player career** and the **World Club Series** (a fictional 16-club tournament).
- **Match engine**: 4-point tries, 2-point conversions and penalty goals, 1-point field goals, six agains,
  completed sets, forced drop-outs, 40/20s, sin bins and golden point. Simulated NRL matches average about 42 points
  and 7 tries, with golden point in roughly 4% of games.

## Play it

- **Browser**: open `web/index.html`. It is one self-contained file and works offline. Hosted over https it installs
  to a phone's home screen (`manifest.webmanifest` and `sw.js` sit next to it).
- **Expo app**: `npm install`, then `npm start` (or `npm run ios`, `npm run android`, `npm run web`). The app shows
  the game full screen in a WebView; saves live in the WebView's local storage.

## Data

1,100+ players. Club squads are compiled from 2026 public squad reporting and the game's own knowledge of who plays
where. They are not an official register and may contain mistakes or be out of date. Ratings, contracts and values
are game estimates. Where a squad is short, fictional depth players fill it out; smaller Test nations are topped up
with fictional pool players. Every fictional player says so on his profile.

Edit squads in `tools/rosters_nrl.py` and `tools/rosters_sl.py` (one line per player:
`name;role[/role2];nation;rating;birth year;Origin state`).

## Rebuilding

```bash
python3 tools/build_game.py   # rosters -> tools/players.json, patches + engine -> web/index.html
npm run build:game            # refresh game/gameHtml.ts, the copy the app bundles
node tools/smoke.js           # optional: plays full seasons headlessly (needs Playwright)
```

`tools/touchline-engine.js` and `tools/shell.html` are the Touchline engine and page shell. `tools/patches/` turns
them into rugby league, in order: positions and the 17-man matchday, tactics, the match engine, club competitions,
the player career, internationals and Origin, the help page, on-screen text and branding.
