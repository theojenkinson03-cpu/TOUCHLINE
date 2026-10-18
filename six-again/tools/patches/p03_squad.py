"""The 17-man matchday and 24-man tournament squads everywhere, plus selection, cover and the squad market basics."""
import re

def apply(js, rep, resub, replace_function):
    N = None
    js = resub(js, r'\{length:23\}', '{length:SQ17}', N, 'len23')
    js = resub(js, r'\b(i|k|idx)<23\b', r'\1<SQ17', N, 'lt23')
    js = resub(js, r'slice\(0,23\)', 'slice(0,SQ17)', N, 'sl023')
    js = resub(js, r'slice\(0,15\)', 'slice(0,XIII)', N, 'sl015')
    js = resub(js, r'slice\(15,23\)', 'slice(XIII,SQ17)', N, 'sl1523')
    js = resub(js, r'slice\(15\)', 'slice(XIII)', N, 'sl15')
    js = resub(js, r'\b(i|idx)<15\b', r'\1<XIII', N, 'lt15')
    js = resub(js, r'\b(i|j)>=15\b', r'\1>=XIII', N, 'ge15')
    js = resub(js, r'\bi===15\b', 'i===XIII', N, 'eq15')
    js = rep(js, 'for(let k=15;k<SQ17;k++)', 'for(let k=XIII;k<SQ17;k++)')
    js = rep(js, '[14]??99', '[XIII-1]??99')
    js = rep(js, '[14]||80', '[XIII-1]||80')
    js = rep(js, 'available(team).length<23&&added<23', 'available(team).length<SQ17&&added<SQ17')
    js = rep(js, 'X.avail<=23', 'X.avail<=SQ17')
    js = rep(js, 'pool(s.team).length<=23', 'pool(s.team).length<=SQ17', 3)
    js = rep(js, "cnt[n]>=23", "cnt[n]>=SQ17")
    js = rep(js, "x.n<23", "x.n<SQ17", 2)
    js = rep(js, "fill([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]);fill([15,16,17,18,19,20,21,22]);return out", "fill([0,1,2,3,4,5,6,7,8,9,10,11,12]);fill([13,14,15,16]);return out")
    js = rep(js, "rows=[[0,1,2],[3,4],[5,6,7],[8,9],[10,11,12,13],[14]]", "rows=[[7,8,9],[10,12,11],[6,5],[4,3,2,1],[0]]")
    # Words around the matchday number.
    js = resub(js, r'(?<=[A-Za-z\-’] )23\b(?![\d%]|\.\d)(?! or under)', '17', N, 'txt23')
    js = js.replace('aged 17 or under', 'aged 23 or under')
    js = rep(js, 'for(let i=15;i<ids.length;i++)if(ids[i])', 'for(let i=XIII;i<ids.length;i++)if(ids[i])')
    js = rep(js, '1–15 start, 16–23 on the bench', '1–13 start, 14–17 on the bench')
    js = resub(js, r'\bstarting XV\b', 'starting 13', N, 'xv')
    js = resub(js, r'\bXV\b', '13', N, 'xv2')
    # 24-man tournament squads (the Rugby League World Cup allows 24).
    def r33(m):
        pre = js_ref[max(0, m.start() - 10):m.start()]
        post = js_ref[m.end():m.end() + 5]
        if re.search(r'age|ageY\(o\.p\)|w:|dist-|be $', pre) or post.startswith(':1.5'):
            return m.group(0)
        return '24'
    js_ref = js
    js = re.sub(r'(?<![.\d#\w])33(?![.\d%\w])', r33, js)
    js = rep(js, 'name your 24 and take on the other 17 nations in Australia', 'name your 24 and take on the rest of the world in Australia')
    # Squad-size rules and quotas for 24-man squads.
    js = resub(js, r"^function squadIssues\(ids\).*$", lambda m: "function squadIssues(ids){const c=coverage(ids),req={PR:3,HK:2,SR:3,LK:1,HB:1,FE:1,CE:2,OB:4};const errors=[];if(ids.length!==24)errors.push(`Select exactly 24 players (${ids.length} selected).`);for(const [p,n] of Object.entries(req)){if((c[p]||0)<n)errors.push(`Need at least ${n} ${LABELS[p].toLowerCase()}.`)}return errors}", 1, 'squadissues', re.M)
    js = rep(js, "const quota={PR:6,HK:3,LK:4,BR:6,SH:3,FH:2,CE:4,OB:5};", "const quota={PR:4,HK:2,SR:4,LK:2,HB:2,FE:2,CE:3,OB:5};")
    js = rep(js, "const MAX_SQUAD=55,POS_MIN={PR:5,HK:3,LK:3,BR:4,SH:2,FH:2,CE:3,OB:4};", "const MAX_SQUAD=36,POS_MIN={PR:5,HK:2,SR:4,LK:2,HB:2,FE:2,CE:3,OB:5};")
    js = resub(js, r"^const ROLE_GAP=.*?\n(?=const FORWARD_ROLES)", lambda m: ROLE_GAP + '\n', 1, 'rolegap', re.M | re.S)
    js = rep(js, "const FORWARD_ROLES=new Set(['LHP','THP','HK','LK','BF','OF','N8']);", "const FORWARD_ROLES=new Set(['PR','HK','SR','LK']);")
    js = rep(js, "function roleOf(p){return p&&ROLE_GROUP[p.role]===p.pos?p.role:(GROUP_ROLES[p?.pos]||['BF'])[0]}", "function roleOf(p){return p&&ROLE_GROUP[p.role]===p.pos?p.role:(GROUP_ROLES[p?.pos]||['SR'])[0]}")
    js = resub(js, r"^const ROLE_PROFILE=.*$", lambda m: "const ROLE_PROFILE={PR:{setpiece:.65,defence:.25,attack:.1},HK:{discipline:.3,pace:.25,attack:.25,defence:.2},SR:{defence:.35,attack:.3,pace:.2,setpiece:.15},LK:{defence:.4,setpiece:.3,attack:.2,kicking:.1},HB:{kicking:.5,attack:.3,discipline:.2},FE:{attack:.5,pace:.25,kicking:.25},CE:{attack:.4,pace:.3,defence:.3},WG:{pace:.55,attack:.35,setpiece:.1},FB:{pace:.4,attack:.35,kicking:.25}};", 1, 'roleprofile', re.M)
    js = resub(js, r"^const SECOND_OPTIONS=.*$", lambda m: "const SECOND_OPTIONS={PR:{LK:0,SR:.6},HK:{HB:0,LK:.4},SR:{LK:0,CE:.5,PR:.8},LK:{SR:0,PR:.5,HK:.9},HB:{FE:0,HK:.6},FE:{HB:0,FB:.4,CE:1},CE:{WG:0,SR:.6,FB:.8},WG:{FB:0,CE:.2},FB:{WG:0,FE:.5,CE:.9}};", 1, 'secondopts', re.M)
    js = rep(js, "for(const [r,prior] of Object.entries(SECOND_OPTIONS[role]||{BF:0}))", "for(const [r,prior] of Object.entries(SECOND_OPTIONS[role]||{SR:0}))")
    js = rep(js, "function assessRoles(p,club,s=game()){const opts=GROUP_ROLES[p.pos]||['BF'];", "function assessRoles(p,club,s=game()){const opts=GROUP_ROLES[p.pos]||['SR'];")
    js = rep(js, "if(!GROUP_ROLES[p.pos])p.pos=db&&GROUP_ROLES[db.pos]?db.pos:p.pos==='BACK'?'CE':'BR';", "if(!GROUP_ROLES[p.pos])p.pos=db&&GROUP_ROLES[db.pos]?db.pos:p.pos==='BACK'?'CE':'SR';")
    # League wages and caps.
    js = resub(js, r"^function fairWage\(p\).*$", lambda m: "function fairWage(p){const o=overall(p),w=o<=60?90000:o<=80?90000+(o-60)*13000:350000+(o-80)*45000+Math.max(0,o-84)**2*8000;return Math.round(w*(isStar(p)?1.1:1)/1000)*1000}", 1, 'fairwage', re.M)
    js = rep(js, "const LEAGUE_CAP={super:7e6,urc:8e6,prem:7e6,top14:9e6};", "const LEAGUE_CAP={nrl:13.5e6,sl:7e6};")
    js = rep(js, "return Math.round((LEAGUE_CAP[leagueFor(team)]||7e6)*1.02**", "return Math.round((LEAGUE_CAP[leagueFor(team)]||7e6)*1.025**")
    js = rep(js, "function emptyTable(teams){return Object.fromEntries(teams.map(t=>[t,{name:t,p:0,w:0,d:0,l:0,pf:0,pa:0,tf:0,ta:0,bp:0,pts:0,last5:[]}]))}", "function emptyTable(teams){return Object.fromEntries(teams.map(t=>[t,{name:t,p:0,w:0,d:0,l:0,pf:0,pa:0,tf:0,ta:0,bp:0,pts:0,byes:0,last5:[]}]))}")
    js = rep(js, "posSlots=[['PR',2],['HK',1],['LK',2],['BR',3],['SH',1],['FH',1],['CE',2],['OB',3]]", "posSlots=[['OB',3],['CE',2],['FE',1],['HB',1],['PR',2],['HK',1],['SR',2],['LK',1]]")
    js = rep(js, "s.lineup=autoLineup(team)}else{s.table=emptyTable(NATIONS);", "s.lineup=autoLineup(team)}else{s.table=emptyTable(NATIONS);")
    js = rep(js, '))} 23.`', '))} 17.`')
    js = rep(js, '))} 23</h2>', '))} 17</h2>')
    js = rep(js, 'Only ${23-short} players', 'Only ${SQ17-short} players')
    return js

ROLE_GAP = r"""const ROLE_GAP={'PR>LK':4,'LK>PR':5,'PR>SR':9,'SR>PR':9,'SR>LK':3,'LK>SR':3,'HK>LK':8,'LK>HK':12,'PR>HK':16,'SR>HK':15,'HK>PR':14,'HK>SR':12,
 'HK>HB':6,'HB>HK':8,'HB>FE':4,'FE>HB':5,'FE>FB':6,'FB>FE':7,'HB>FB':12,'FE>CE':8,'CE>FE':12,
 'CE>WG':3,'WG>CE':4,'CE>FB':7,'FB>CE':5,'WG>FB':4,'FB>WG':2,'CE>SR':8,'SR>CE':9,'LK>FE':16,'LK>HB':18,'HK>FE':14};"""
