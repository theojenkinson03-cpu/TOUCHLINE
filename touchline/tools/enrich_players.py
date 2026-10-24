#!/usr/bin/env python3
"""Fill gaps in Touchline's player database from Wikidata, and fetch freely licensed headshots from Wikimedia Commons.

Nothing is invented. A player is matched to a Wikidata item only when the name matches exactly (accents and case aside),
the item is a rugby union player, and at least one independent check agrees: his club, his national team or his date of
birth. Ambiguous or contradicting candidates are skipped and listed in the review file instead.

Only fields the game does not already have are filled: date of birth (to the day), nationality (from a senior national
team he has played for), Test caps, height and weight. Every filled player keeps his Wikidata ID, so each value can be
checked at its source.

Photos come only from Commons and only under a free licence (public domain, CC0, CC BY or CC BY-SA). Each one keeps its
author, licence and file page, which the game shows in its credits. A face is found in each image and the crop is
centred on it; if no face is found the photo is not used.

Usage:
    python3 enrich_players.py --html ../index.html --out .          # data and photos
    python3 enrich_players.py --html ../index.html --out . --no-photos
Outputs, in --out:
    enrichment.json  per-player fields and their Wikidata IDs
    photos.json      per-player headshot (WebP data URI) with author, licence and file page
    review.csv       every player that was not matched, and why

Needs network access to query.wikidata.org, commons.wikimedia.org and upload.wikimedia.org.
Photo cropping needs Pillow and OpenCV 4 (pip install pillow "opencv-python-headless<5"; OpenCV 5 dropped the face detector).
"""
import argparse, base64, csv, io, json, os, re, ssl, sys, time, unicodedata, urllib.parse, urllib.request
from datetime import date

UA = 'TouchlineGameData/1.0 (offline rugby management game; one-off enrichment run; https://github.com/theojenkinson03-cpu/closer-2)'
SPARQL = 'https://query.wikidata.org/sparql'
COMMONS = 'https://commons.wikimedia.org/w/api.php'
RUGBY_UNION = 'Q5849'          # sport: rugby union
RU_PLAYER = 'Q14089670'        # occupation: rugby union player
FREE_LICENCE = re.compile(r'^(cc0|public domain|pd\b.*|cc by(-sa)? \d(\.\d)?(\s.*)?)$', re.I)
NATIONS = ['New Zealand', 'Australia', 'South Africa', 'Argentina', 'England', 'Ireland', 'Scotland', 'Wales', 'France', 'Italy',
           'Fiji', 'Samoa', 'Tonga', 'Japan', 'Georgia', 'Canada', 'United States', 'Uruguay', 'Chile', 'Romania', 'Spain',
           'Portugal', 'Hong Kong', 'Zimbabwe', 'Namibia', 'Russia', 'Germany', 'Netherlands', 'Belgium', 'Kenya', 'Brazil']
# Wikidata position labels to the game's eight position groups
POS_WORDS = [('PR', ('prop',)), ('HK', ('hooker',)), ('LK', ('lock',)), ('BR', ('flanker', 'number eight', 'number 8', 'back row', 'loose forward')),
             ('SH', ('scrum-half', 'scrum half', 'halfback')), ('FH', ('fly-half', 'fly half', 'first five', 'outside half', 'stand-off')),
             ('CE', ('centre', 'center', 'second five')), ('OB', ('wing', 'fullback', 'full-back', 'full back', 'outside back'))]
CLUB_NOISE = {'rugby', 'rfc', 'rc', 'fc', 'club', 'union', 'team', 'the', 'football', 'sporting', 'de', 'du', 'la', 'le', 'stade'}


def norm(s):
    """Lower case, no accents, letters and digits only, single spaces."""
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode()
    s = re.sub(r"['’`]", '', s.lower())
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


ABBREV = {'nsw': 'new south wales', 'qld': 'queensland', 'wp': 'western province', 'asm': 'clermont', 'ubb': 'bordeaux begles'}


def club_tokens(s):
    """A club's distinctive words: no disambiguation in brackets, no 'Rugby', 'RFC' or 'Stade', short forms written out."""
    s = re.sub(r'\(.*?\)', ' ', str(s or ''))
    words = ' '.join(ABBREV.get(t, t) for t in norm(s).split()).split()
    return frozenset(t for t in words if t not in CLUB_NOISE and len(t) > 1)


def club_match(ours, theirs):
    """True only when a Wikidata team label names exactly the same club as ours, once the generic words are set aside.
    'Leinster' ~ 'Leinster Rugby' and 'NSW Waratahs' ~ 'New South Wales Waratahs', but 'Sharks' is not 'Sale Sharks'
    and 'Lions' is not 'British & Irish Lions'."""
    a, b = club_tokens(ours), club_tokens(theirs)
    return bool(a) and a == b


def national_team(label):
    """The nation a senior national team label belongs to, or None (under-20s, sevens, A sides and women's teams are ignored)."""
    l = label.lower()
    if 'national' not in l or any(w in l for w in ('under', 'u20', 'u-20', 'u21', 'sevens', ' 7s', ' a ', "women", 'emerging', 'xv ', 'barbarians', 'schools', 'students', 'universit')):
        return None
    for n in NATIONS:
        if l.startswith(n.lower() + ' national'):
            return n
    return None


def pos_group(labels):
    out = set()
    for lab in labels:
        l = lab.lower()
        for code, words in POS_WORDS:
            if any(w in l for w in words):
                out.add(code)
    return out


def to_cm(amount, unit):
    v = float(amount)
    if unit.endswith('Q11573'):    # metre
        v *= 100
    elif unit.endswith('Q218593'):  # inch
        v *= 2.54
    elif not unit.endswith('Q174728'):  # centimetre
        return None
    return round(v) if 150 <= v <= 220 else None


def to_kg(amount, unit):
    v = float(amount)
    if unit.endswith('Q100995'):  # pound
        v *= 0.45359237
    elif not unit.endswith('Q11570'):  # kilogram
        return None
    return round(v) if 60 <= v <= 170 else None


def score(player, cand):
    """How strongly a Wikidata candidate is the same man as our player. None means a contradiction (reject)."""
    s, why = 0, []
    if player.get('dob') and cand.get('dob'):
        if player['dob'][:10] != cand['dob']:
            return None, ['birth date differs']
        s += 3; why.append('birth date')
    clubs = [player.get('club'), player.get('sourceClub')]
    if any(c and club_match(c, t) for c in clubs for t in cand['teams']):
        s += 3; why.append('club')
    nats = {n for n in (national_team(t) for t in cand['teams']) if n}
    if player.get('nation') and player['nation'] in nats:
        s += 2; why.append('national team')
    elif player.get('nation') and nats and player['nation'] not in nats:
        s -= 2; why.append('different national team')
    pg = pos_group(cand['positions'])
    ours = {player.get('pos')}
    if pg:
        if ours & pg:
            s += 1; why.append('position')
        elif not ({'CE', 'OB'} & ours and {'CE', 'OB'} & pg) and not ({'LK', 'BR'} & ours and {'LK', 'BR'} & pg):
            s -= 2; why.append('different position')
    return s, why


def choose(player, cands):
    """The single convincing candidate, or None with a reason."""
    scored = []
    for c in cands:
        sc, why = score(player, c)
        if sc is not None:
            scored.append((sc, why, c))
    if not scored:
        return None, 'every candidate contradicts the game (birth date)' if cands else 'no Wikidata rugby union player with this name'
    scored.sort(key=lambda x: -x[0])
    best = scored[0]
    if best[0] < 2:
        return None, f'not enough agreement ({", ".join(best[1]) or "name only"})'
    if len(scored) > 1 and scored[1][0] > best[0] - 2:
        return None, f'{len(scored)} candidates too close to call'
    return best[2] | {'why': best[1]}, None


# ---------------------------------------------------------------- network

def ctx():
    c = ssl.create_default_context()
    for k in ('SSL_CERT_FILE', 'REQUESTS_CA_BUNDLE'):
        if os.environ.get(k) and os.path.exists(os.environ[k]):
            c.load_verify_locations(os.environ[k])
    return c


def get(url, data=None, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={'User-Agent': UA, 'Accept': 'application/sparql-results+json, application/json, */*'})
            with urllib.request.urlopen(req, timeout=90, context=ctx()) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 - retried, then raised
            if i == tries - 1:
                raise
            time.sleep(2 ** (i + 1))


def sparql(q):
    body = urllib.parse.urlencode({'query': q, 'format': 'json'}).encode()
    return json.loads(get(SPARQL, data=body))['results']['bindings']


def candidates(names):
    """Wikidata rugby union players whose English or French label or alias is one of these names."""
    vals = ' '.join(f'"{n}"@en "{n}"@fr' for n in (x.replace('\\', '').replace('"', '') for x in names))
    q = f'''SELECT ?item ?name ?dob ?prec ?h ?hu ?m ?mu ?img (GROUP_CONCAT(DISTINCT ?teamL; separator="|") AS ?teams)
      (GROUP_CONCAT(DISTINCT CONCAT(?teamL, "#", STR(?caps)); separator="|") AS ?capsBy) (GROUP_CONCAT(DISTINCT ?posL; separator="|") AS ?pos) WHERE {{
      VALUES ?name {{ {vals} }}
      ?item rdfs:label|skos:altLabel ?name; wdt:P31 wd:Q5.
      {{ ?item wdt:P641 wd:{RUGBY_UNION} }} UNION {{ ?item wdt:P106 wd:{RU_PLAYER} }}
      OPTIONAL {{ ?item p:P569/psv:P569 [wikibase:timeValue ?dob; wikibase:timePrecision ?prec] }}
      OPTIONAL {{ ?item p:P2048/psv:P2048 [wikibase:quantityAmount ?h; wikibase:quantityUnit ?hu] }}
      OPTIONAL {{ ?item p:P2067/psv:P2067 [wikibase:quantityAmount ?m; wikibase:quantityUnit ?mu] }}
      OPTIONAL {{ ?item wdt:P18 ?img }}
      OPTIONAL {{ ?item p:P54 ?st. ?st ps:P54 ?team. ?team rdfs:label ?teamL. FILTER(LANG(?teamL)="en") OPTIONAL {{ ?st pq:P1350 ?caps }} }}
      OPTIONAL {{ ?item wdt:P413 ?p. ?p rdfs:label ?posL. FILTER(LANG(?posL)="en") }}
    }} GROUP BY ?item ?name ?dob ?prec ?h ?hu ?m ?mu ?img'''
    out = {}
    for b in sparql(q):
        v = lambda k: b.get(k, {}).get('value')
        qid = v('item').rsplit('/', 1)[1]
        c = out.setdefault((norm(v('name')), qid), {'qid': qid, 'teams': set(), 'positions': set(), 'caps': {}, 'dob': None, 'h': None, 'm': None, 'img': None})
        if v('dob') and v('prec') == '11':
            c['dob'] = v('dob')[:10]
        if v('h') and not c['h']:
            c['h'] = to_cm(v('h'), v('hu') or '')
        if v('m') and not c['m']:
            c['m'] = to_kg(v('m'), v('mu') or '')
        if v('img') and not c['img']:
            c['img'] = urllib.parse.unquote(v('img').rsplit('/', 1)[1])
        c['teams'] |= {t for t in (v('teams') or '').split('|') if t}
        c['positions'] |= {t for t in (v('pos') or '').split('|') if t}
        for tc in (v('capsBy') or '').split('|'):
            if '#' in tc and tc.split('#', 1)[1].strip():
                t, n = tc.split('#', 1)
                try:
                    c['caps'][t] = max(c['caps'].get(t, 0), int(float(n)))
                except ValueError:
                    pass
    by = {}
    for (n, _), c in out.items():
        by.setdefault(n, []).append(c)
    return by


def commons_info(files):
    """Licence, author and a 400px thumbnail URL for up to 50 Commons files."""
    titles = '|'.join('File:' + f for f in files)
    q = urllib.parse.urlencode({'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'iiprop': 'url|extmetadata', 'iiurlwidth': 400, 'titles': titles})
    data = json.loads(get(COMMONS + '?' + q))
    norm_map = {n['to']: n['from'] for n in data.get('query', {}).get('normalized', [])}
    out = {}
    for page in data.get('query', {}).get('pages', {}).values():
        ii = (page.get('imageinfo') or [None])[0]
        if not ii:
            continue
        md = ii.get('extmetadata', {})
        lic = (md.get('LicenseShortName', {}).get('value') or '').strip()
        artist = re.sub(r'<[^>]+>', '', md.get('Artist', {}).get('value') or '').strip()
        title = norm_map.get(page['title'], page['title'])
        out[title.split(':', 1)[1]] = {'thumb': ii.get('thumburl'), 'page': ii.get('descriptionurl'), 'license': lic,
                                       'licenseUrl': md.get('LicenseUrl', {}).get('value'), 'author': artist or 'Unknown author'}
    return out


def face_crop(raw, w=96, h=120):
    """A head-and-shoulders WebP centred on the largest face, or None if there is no clear face."""
    import cv2, numpy as np
    from PIL import Image
    img = Image.open(io.BytesIO(raw)).convert('RGB')
    arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    det = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = det.detectMultiScale(arr, scaleFactor=1.1, minNeighbors=6, minSize=(36, 36))
    if len(faces) == 0:
        return None
    x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
    if fw < img.width * 0.08:   # a face in a crowd or a wide action shot: not a headshot
        return None
    cw = fw * 2.4
    ch = cw * h / w
    cx, cy = x + fw / 2, y + fh * 0.9
    left, top = max(0, cx - cw / 2), max(0, cy - ch * 0.42)
    right, bottom = min(img.width, left + cw), min(img.height, top + ch)
    crop = img.crop((int(left), int(top), int(right), int(bottom))).resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    crop.save(buf, 'WEBP', quality=72, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------- run

def load_players(html):
    s = open(html, encoding='utf-8').read()
    m = re.search(r'<script id="database" type="application/json">(.*?)</script>', s, re.S)
    return json.loads(m.group(1).replace('<\\/', '</'))['players']


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--html', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--no-photos', action='store_true')
    ap.add_argument('--batch', type=int, default=40)
    a = ap.parse_args()
    players = [p for p in load_players(a.html) if 'Fictional' not in (p.get('source') or '')]
    names = sorted({p['name'] for p in players})
    found = {}
    for i in range(0, len(names), a.batch):
        found.update(candidates(names[i:i + a.batch]))
        print(f'Wikidata: {min(i + a.batch, len(names))}/{len(names)} names', file=sys.stderr)
        time.sleep(1)
    enrich, review, matched = {}, [], {}
    for p in players:
        c, why = choose(p, found.get(norm(p['name']), []))
        if not c:
            review.append({'id': p['id'], 'name': p['name'], 'club': p['club'], 'reason': why})
            continue
        matched[p['id']] = c
        e = {'wd': c['qid'], 'matchedOn': c['why']}
        if not p.get('dob') and c['dob']:
            e['dob'] = c['dob']
        nats = sorted({n for n in (national_team(t) for t in c['teams']) if n})
        if not p.get('nation') and len(nats) == 1:
            e['nation'] = nats[0]
        nat = p.get('nation') or e.get('nation')
        caps = [n for t, n in c['caps'].items() if national_team(t) == nat]
        if p.get('caps') is None and caps:
            e['caps'] = max(caps)
        if c['h']:
            e['heightCm'] = c['h']
        if c['m']:
            e['weightKg'] = c['m']
        enrich[p['id']] = e
    os.makedirs(a.out, exist_ok=True)
    meta = {'generated': date.today().isoformat(), 'source': 'Wikidata (CC0), matched by name plus club, national team or birth date',
            'players': len(players), 'matched': len(enrich), 'dob': sum('dob' in e for e in enrich.values()),
            'nation': sum('nation' in e for e in enrich.values()), 'caps': sum('caps' in e for e in enrich.values()),
            'height': sum('heightCm' in e for e in enrich.values()), 'weight': sum('weightKg' in e for e in enrich.values())}
    photos = {}
    if not a.no_photos:
        want = {pid: c['img'] for pid, c in matched.items() if c.get('img')}
        files = sorted(set(want.values()))
        info = {}
        for i in range(0, len(files), 50):
            info.update(commons_info(files[i:i + 50]))
            time.sleep(1)
        for pid, f in want.items():
            meta_f = info.get(f)
            if not meta_f or not meta_f['thumb'] or not FREE_LICENCE.match(meta_f['license']):
                review.append({'id': pid, 'name': next(p['name'] for p in players if p['id'] == pid), 'club': '', 'reason': f'photo skipped: licence "{meta_f and meta_f["license"]}"'})
                continue
            try:
                img = face_crop(get(meta_f['thumb']))
            except Exception as e:  # noqa: BLE001
                img = None
            if not img:
                continue
            photos[pid] = {'img': img, 'file': f, 'page': meta_f['page'], 'author': meta_f['author'][:120], 'license': meta_f['license'], 'licenseUrl': meta_f['licenseUrl']}
            time.sleep(.2)
        meta['photos'] = len(photos)
    json.dump({'meta': meta, 'players': enrich}, open(os.path.join(a.out, 'enrichment.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    if not a.no_photos:
        json.dump(photos, open(os.path.join(a.out, 'photos.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(a.out, 'review.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['id', 'name', 'club', 'reason'])
        w.writeheader()
        w.writerows(review)
    print(json.dumps(meta, indent=1))


if __name__ == '__main__':
    main()
