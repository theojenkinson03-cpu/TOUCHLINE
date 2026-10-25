# Touchline data tools

## `enrich_players.py`: fill gaps in the player database and add player photos

Touchline's squads come from published 2026 squad lists, which often leave out a player's date of birth, nationality or
Test caps. This tool fills those gaps from [Wikidata](https://www.wikidata.org) (CC0) and adds a head-and-shoulders photo
for players who have a freely licensed picture on [Wikimedia Commons](https://commons.wikimedia.org).

### What it does

- **Matches carefully.** A player is matched to a Wikidata item only when all of these hold:
  - the name matches exactly, ignoring accents and capitals;
  - the item is a rugby union player;
  - at least one independent check agrees: his club, a senior national team he played for, or his date of birth.

  A contradicting birth date, a different national team or a clearly different position counts against a candidate.
  Two candidates that are too close to call are both skipped.
- **Fills only what is missing.** It fills empty fields only: date of birth (to the day), nationality (from a senior
  national team he has played for) and Test caps. It also adds height and weight. Every matched player keeps his Wikidata
  ID, and the game links to it from the player's profile.
- **Uses only free photos.** Photos must be public domain, CC0, CC BY or CC BY-SA. Each crop is centred on a detected face,
  and a picture with no clear face is not used. The game shows every photo's author, licence and file page, on the
  profile and under Photo credits in the guide.
- **Lists what it skipped.** Everything not matched is written to `review.csv` with the reason.

### Running it

It needs network access to `query.wikidata.org`, `www.wikidata.org`, `commons.wikimedia.org` and `upload.wikimedia.org`.

```
pip install pillow "opencv-python-headless<5"     # OpenCV 5 dropped the face detector
cd touchline/tools
python3 enrich_players.py --html ../index.html --out .
```

It writes these files next to itself:

| File | Contents |
| --- | --- |
| `enrichment.json` | The filled fields, keyed by player ID |
| `photos.json` | The photos with their credits |
| `review.csv` | Every player it skipped, and why |

The game build merges the first two into `index.html` when they are present. Use `--no-photos` for the data only.

### Club crests

Official club and union logos are trademarks and are not freely licensed, so the game does not ship them. It draws its
own badge for every club. To use real crests on your own device, choose a folder of images in Settings → Your data →
Import a folder. Files named after a club become its crest and files named after a player become his photo. They stay
in your browser and are never put in a save.
