"""Builds the 6 Again player database (JSON) from the roster files."""
import json, random, re, sys, unicodedata, collections, os
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'rosters_nrl.py')).read())
exec(open(os.path.join(HERE, 'rosters_sl.py')).read())

NAT = {'AUS': 'Australia', 'NZL': 'New Zealand', 'TGA': 'Tonga', 'SAM': 'Samoa', 'PNG': 'Papua New Guinea', 'FIJ': 'Fiji',
       'COK': 'Cook Islands', 'ENG': 'England', 'FRA': 'France', 'WAL': 'Wales', 'SCO': 'Scotland', 'IRE': 'Ireland',
       'LEB': 'Lebanon', 'ITA': 'Italy'}
NATIONS = ['Australia', 'New Zealand', 'England', 'Tonga', 'Samoa', 'Papua New Guinea', 'Fiji', 'Cook Islands', 'France',
           'Lebanon', 'Wales', 'Ireland', 'Scotland', 'Italy']
GROUP = {'FB': 'OB', 'WG': 'OB', 'CE': 'CE', 'FE': 'FE', 'HB': 'HB', 'HK': 'HK', 'PR': 'PR', 'SR': 'SR', 'LK': 'LK'}
SECOND = {'FB': ['WG', 'FE', 'CE'], 'WG': ['FB', 'CE'], 'CE': ['WG', 'SR', 'FB'], 'FE': ['HB', 'FB', 'CE'], 'HB': ['FE', 'HK'],
          'HK': ['HB', 'LK'], 'PR': ['LK', 'SR'], 'SR': ['LK', 'CE', 'PR'], 'LK': ['SR', 'PR', 'HK']}
SEASON = 2026

def slug(name):
    s = unicodedata.normalize('NFD', name)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z]', '', s.lower())

def fair_wage(o):
    w = 90000 if o <= 60 else 90000 + (o - 60) * 13000 if o <= 80 else 350000 + (o - 80) * 45000 + max(0, o - 84) ** 2 * 8000
    return round(w * (1.1 if o >= 90 else 1) / 1000) * 1000

rng = random.Random(2026)
players, ids = [], set()

def add(name, role, role2, nation, club, base, born, state, source, group, league):
    pid = slug(name)
    n = 1
    while pid in ids:
        n += 1
        pid = slug(name) + str(n)
    ids.add(pid)
    age = SEASON - born
    pot = base + (max(0, 24 - age) * 1.6 + rng.random() * 3 if age <= 25 else rng.random() * 1.5)
    pot = min(95, round(pot))
    wage = fair_wage(base) * (0.55 if league == 'sl' else 1 if league == 'nrl' else 0.25)
    wage = round(wage / 1000) * 1000
    if not role2:
        role2 = SECOND[role][int(rng.random() * len(SECOND[role]) * 0.999)]
    p = {'id': pid, 'name': name, 'pos': GROUP[role], 'nation': nation, 'club': club, 'source': source,
         'dob': str(born), 'caps': None, 'group': group, 'nationalVerified': False, 'base': base, 'potential': max(base, pot),
         'form': 0, 'growth': 0, 'fitness': 100, 'apps': 0, 'lastRating': None, 'history': [],
         'years': 1 + int(rng.random() * 3.4), 'wage': wage, 'ask': wage, 'morale': 70, 'sourceClub': club,
         'role': role, 'role2': role2}
    if state:
        p['origin'] = state
    players.append(p)
    return p

REAL_SRC = {'nrl': 'NRL 2026 squad (compiled from public reporting; rating is a game estimate)',
            'sl': 'Super League 2026 squad (compiled from public reporting; rating is a game estimate)'}
for league, table in (('nrl', NRL), ('sl', SL)):
    for club, block in table.items():
        for line in block.strip().split('\n'):
            name, roles, nat, rating, born, state = line.split(';')
            r1, _, r2 = roles.partition('/')
            add(name, r1, r2 or None, NAT[nat], club, int(rating), int(born), state or None, REAL_SRC[league], 'Senior', league)

POOLS = {
    'Australia': (['Jack', 'Lachlan', 'Cooper', 'Mitchell', 'Brodie', 'Jayden', 'Kye', 'Tyler', 'Bailey', 'Riley', 'Harrison', 'Zac', 'Jett', 'Hayden', 'Nate', 'Corey', 'Blake', 'Kurtis'],
                  ['Hartley', 'Mullins', 'Gallagher', 'Doherty', 'Sheridan', 'Corbett', 'Pringle', 'Lockyer-Hale', 'Fenwick', 'Rourke', 'Kearney', 'Whitbread', 'Dwyer', 'Cassidy', 'McKellar', 'Brennan', 'Tolhurst', 'Ashby']),
    'New Zealand': (['Nikau', 'Tama', 'Wiremu', 'Kauri', 'Rawiri', 'Te Rangi', 'Manaia', 'Kaleb', 'Ihaia', 'Hemi', 'Tai', 'Ari'],
                    ['Ngata', 'Parata', 'Henare', 'Tawhiri', 'Rewiti', 'Kereama', 'Paewai', 'Wihongi', 'Tipene', 'Matenga', 'Pomare', 'Ruka']),
    'Tonga': (['Sione', 'Tevita', 'Viliami', 'Siosaia', 'Semisi', 'Ofa', 'Lisiate', 'Feleti', 'Taniela', 'Paula', 'Mosese', 'Sitani'],
              ['Fifita', 'Havili', 'Moala', 'Taufa', 'Vainikolo', 'Tupou', 'Kata', 'Lolohea', 'Fonua', 'Maka', 'Halaholo', 'Veikune']),
    'Samoa': (['Iosefa', 'Fetu', 'Lotu', 'Mose', 'Pita', 'Losi', 'Junior', 'Toa', 'Malakai', 'Faalogo', 'Ioane', 'Sefo'],
              ['Leota', 'Fonoti', 'Sapolu', 'Faleolo', 'Tuimavave', 'Lealaiauloto', 'Aumua', 'Seumanu', 'Tuilagi', 'Masoe', 'Pouono', 'Esera']),
    'Papua New Guinea': (['Rhadley', 'Junior', 'Kyle', 'Emmanuel', 'Nixon', 'Benji', 'Judah', 'Solomon', 'Wartovo', 'Keven', 'Morea', 'Brendan'],
                         ['Kambua', 'Wapi', 'Kua', 'Waninga', 'Bogi', 'Kumung', 'Opa', 'Simon', 'Lasu', 'Moka', 'Nebauka', 'Tambu']),
    'Fiji': (['Semi', 'Josua', 'Waisake', 'Viliame', 'Isikeli', 'Sireli', 'Jone', 'Meli', 'Apisai', 'Kitione', 'Ratu', 'Pio'],
             ['Ravai', 'Tabua', 'Vosa', 'Koroi', 'Seru', 'Cakau', 'Waqa', 'Naivalu', 'Rokoduru', 'Tamani', 'Delai', 'Vunivalu']),
    'Cook Islands': (['Tepaki', 'Ngatokorua', 'Teariki', 'Tuaine', 'Rua', 'Tangi', 'Maara', 'Tamatoa', 'Mana', 'Teina', 'Tere', 'Akatere'],
                     ['Tangitoru', 'Marsters', 'Tuara', 'Rima', 'Pera', 'Heather', 'Mataio', 'Tuakana', 'Tatuava', 'Pokino', 'Mokoroa', 'Taio']),
    'England': (['Alfie', 'Harvey', 'Ollie', 'Jordan', 'Kieran', 'Callum', 'Danny', 'Ben', 'Reece', 'Lewis', 'Owen', 'Jake', 'Tom', 'Sam'],
                ['Hargreaves', 'Ashworth', 'Thornton', 'Pickering', 'Rowbotham', 'Haigh', 'Greenhalgh', 'Sutcliffe-Hall', 'Brierley', 'Ackroyd', 'Holden', 'Barraclough', 'Kershaw', 'Whitworth']),
    'France': (['Louis', 'Hugo', 'Théo', 'Mathis', 'Lucas', 'Romain', 'Baptiste', 'Clément', 'Maxime', 'Jules', 'Enzo', 'Florian'],
               ['Bertrand', 'Fabre', 'Escaré', 'Garcia', 'Vidal', 'Roques', 'Sabatier', 'Py', 'Barthes', 'Cazals', 'Fournier', 'Mas']),
    'Lebanon': (['Elias', 'Joseph', 'Charbel', 'Anthony', 'Michael', 'Rabih', 'Jamil', 'Josh', 'Karim', 'Fadi', 'George', 'Nathan'],
                ['Habib', 'Khoury', 'Haddad', 'Nassar', 'Saleh', 'Mansour', 'Rahme', 'Fakhoury', 'Kassis', 'Daher', 'Boutros', 'Tannous']),
    'Wales': (['Rhys', 'Gethin', 'Dafydd', 'Osian', 'Tomos', 'Ieuan', 'Morgan', 'Elis', 'Cai', 'Harri', 'Steffan', 'Iwan'],
              ['Pritchard', 'Llewellyn', 'Evans', 'Jenkins', 'Price', 'Rees', 'Griffiths', 'Powell', 'Lloyd', 'Bevan', 'Prosser', 'Vaughan']),
    'Ireland': (['Cian', 'Eoin', 'Oisín', 'Darragh', 'Conor', 'Seán', 'Rory', 'Fionn', 'Cathal', 'Niall', 'Ronan', 'Aidan'],
                ['Byrne', 'Kavanagh', 'Moriarty', 'Doyle', 'Nolan', 'Quinlan', 'Brennan', 'Keogh', 'Hegarty', 'Lynch', 'Duggan', 'Mulcahy']),
    'Scotland': (['Fraser', 'Ewan', 'Callum', 'Hamish', 'Angus', 'Finlay', 'Euan', 'Struan', 'Murray', 'Lewis', 'Cameron', 'Ross'],
                 ['Drummond', 'Munro', 'Dunbar', 'Kerr', 'Buchanan', 'Sinclair', 'McLaren', 'Rennie', 'Gillies', 'Baird', 'Lennox', 'Imrie']),
    'Italy': (['Lorenzo', 'Matteo', 'Alessandro', 'Tommaso', 'Riccardo', 'Francesco', 'Giacomo', 'Pietro', 'Marco', 'Luca', 'Nico', 'Dario'],
              ['Rossi', 'Bianchi', 'Romano', 'Colombo', 'Ricci', 'Marino', 'Greco', 'Gallo', 'Conti', 'Bruno', 'Ferraro', 'Moretti']),
}
CLUB_NATION = {'Wales': 'Wales'}
SL_NATION = 'England'
DEPTH_SRC = 'Fictional depth player (squad depth, not a real player)'
NEED_ROLES = ['PR', 'PR', 'PR', 'HK', 'SR', 'SR', 'LK', 'HB', 'FE', 'CE', 'CE', 'WG', 'WG', 'FB']

def fict_name(nation):
    first, last = POOLS[nation]
    for _ in range(200):
        n = f'{rng.choice(first)} {rng.choice(last)}'
        if slug(n) not in ids:
            return n
    return f'{rng.choice(first)} {rng.choice(last)}-{rng.choice(last)}'

def club_nation(club, league):
    if league == 'sl':
        return 'France' if club in ('Catalans Dragons', 'Toulouse Olympique') else SL_NATION
    if club == 'New Zealand Warriors':
        return 'New Zealand'
    return rng.choice(['Australia'] * 6 + ['New Zealand', 'Tonga', 'Samoa'])

def fill_role(squad):
    have = collections.Counter(p['role'] for p in squad)
    want = collections.Counter(NEED_ROLES * 2)
    gaps = sorted(want, key=lambda r: have[r] - want[r])
    return gaps[0]

for league, table, size, lo, hi in (('nrl', NRL, 30, 62, 71), ('sl', SL, 28, 58, 67)):
    for club in table:
        squad = [p for p in players if p['club'] == club]
        while len(squad) < size:
            nation = club_nation(club, league)
            role = fill_role(squad)
            born = SEASON - rng.choice([18, 19, 19, 20, 20, 21, 22, 23, 24, 26])
            state = rng.choice(['NSW', 'QLD']) if nation == 'Australia' else None
            p = add(fict_name(nation), role, None, nation, club, rng.randint(lo, hi), born, state, DEPTH_SRC, 'Academy depth', league)
            p['potential'] = min(88, p['base'] + rng.randint(3, 14) if SEASON - born <= 22 else p['base'] + rng.randint(0, 3))
            squad.append(p)

DOMESTIC = {'Papua New Guinea': ['PNG Hunters'], 'Fiji': ['Kaiviti Silktails'], 'Cook Islands': ['Cook Islands domestic'],
            'Lebanon': ['Lebanon domestic'], 'France': ['Carcassonne', 'Limoux', 'Lézignan', 'Albi', 'Villeneuve'],
            'Wales': ['Wales domestic'], 'Ireland': ['Ireland domestic'], 'Scotland': ['Scotland domestic'],
            'Italy': ['Italy domestic'], 'Tonga': ['Tonga domestic'], 'Samoa': ['Samoa domestic'],
            'England': ['Championship'], 'New Zealand': ['NZRL domestic'], 'Australia': ['NSW Cup']}
NAT_TARGET = 30
for nation in NATIONS:
    have = [p for p in players if p['nation'] == nation]
    while len(have) < NAT_TARGET:
        role = fill_role(have)
        born = SEASON - rng.randint(19, 30)
        lo, hi = (55, 66) if nation in ('Wales', 'Ireland', 'Scotland', 'Italy', 'Lebanon', 'Cook Islands') else (58, 69)
        p = add(fict_name(nation), role, None, nation, rng.choice(DOMESTIC[nation]), rng.randint(lo, hi), born, None,
                f'Fictional {nation} international pool player (not a real player)', 'Emerging', 'dom')
        have.append(p)

NAT_MIN = {'PR': 6, 'HK': 3, 'SR': 5, 'LK': 3, 'HB': 3, 'FE': 3, 'CE': 4, 'OB': 7}
ROLE_FOR = {'PR': 'PR', 'HK': 'HK', 'SR': 'SR', 'LK': 'LK', 'HB': 'HB', 'FE': 'FE', 'CE': 'CE', 'OB': 'WG'}
for nation in NATIONS:
    for grp, need in NAT_MIN.items():
        have = [p for p in players if p['nation'] == nation and p['pos'] == grp]
        while len(have) < need:
            role = ROLE_FOR[grp] if grp != 'OB' or sum(1 for p in have if p['role'] == 'FB') >= 2 else 'FB'
            lo, hi = (55, 66) if nation in ('Wales', 'Ireland', 'Scotland', 'Italy', 'Lebanon', 'Cook Islands') else (58, 69)
            p = add(fict_name(nation), role, None, nation, rng.choice(DOMESTIC[nation]), rng.randint(lo, hi), SEASON - rng.randint(19, 30), None,
                    f'Fictional {nation} international pool player (not a real player)', 'Emerging', 'dom')
            have.append(p)

clubs_nrl, clubs_sl = list(NRL), list(SL)
meta = {
    'checked': '18 October 2026', 'season': SEASON,
    'clubs': clubs_nrl + clubs_sl, 'nations': NATIONS,
    'clubCounts': dict(collections.Counter(p['club'] for p in players if p['club'] in NRL or p['club'] in SL)),
    'nationCounts': dict(collections.Counter(p['nation'] for p in players)),
    'leagues': {
        'nrl': {'name': 'National Rugby League', 'short': 'NRL', 'teams': clubs_nrl, 'games': 24, 'rounds': 27, 'playoffs': 8},
        'sl': {'name': 'Super League', 'short': 'Super League', 'teams': clubs_sl, 'games': 26, 'rounds': 26, 'playoffs': 6},
    },
    'rosterNotes': {},
    'edition': 'NRL & Super League · October 2026',
}
db = {'players': players, 'meta': meta}
json.dump(db, open(sys.argv[1] if len(sys.argv) > 1 else 'db6.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(players), meta['clubCounts'], meta['nationCounts'], sep='\n')
