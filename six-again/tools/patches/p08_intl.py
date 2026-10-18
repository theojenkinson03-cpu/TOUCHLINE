"""International rugby league: the World Cup format, the yearly calendar, the Ashes, Pacific Championships and State of Origin."""
import re

def line(js, start, new, resub, name):
    return resub(js, r'^' + re.escape(start) + r'.*$', lambda m: new, 1, name, re.M)

def apply(js, rep, resub, replace_function):
    js = line(js, "const WC_HOSTS=", "const WC_HOSTS={2026:'Australia',2030:'England',2034:'New Zealand',2038:'France',2042:'Australia',2046:'England',2050:'New Zealand'};", resub, 'wchosts')
    js = replace_function(js, 'wcHost', "function wcHost(y){return WC_HOSTS[y]||['Australia','England','New Zealand','France'][Math.floor((y-2026)/4)%4]}", 'wchost')
    js = replace_function(js, 'isWCYear', "function isWCYear(y){return (y-2026)%4===0}", 'iswc')
    js = line(js, "const NC_START=", "const NC_START={1:{Pacific:['Australia','New Zealand','Tonga','Samoa','Papua New Guinea'],Europe:['England']},2:{Pacific:['Fiji','Cook Islands'],'Europe & Middle East':['France','Lebanon','Wales','Ireland','Scotland','Italy']}};", resub, 'ncstart')
    js = line(js, "const CONF_RENAME=", "const CONF_RENAME={};", resub, 'confrename')
    js = line(js, "const TIER_NAME=", "const TIER_NAME={1:'Tier 1 Test nation',2:'Emerging Test nation'};", resub, 'tiername')
    js = line(js, "const NAT_REGION=", "const NAT_REGION={England:'EU',France:'EU',Wales:'EU',Ireland:'EU',Scotland:'EU',Italy:'EU',Lebanon:'EU',Australia:'SH','New Zealand':'SH',Tonga:'SH',Samoa:'SH','Papua New Guinea':'SH',Fiji:'SH','Cook Islands':'SH'};", resub, 'natregion')
    js = replace_function(js, 'compName', "function compName(s=game()){const w=curWin(s);if(intlCareer(s)&&w)return `${winCompName(winCompOf(s.team,w,s),w,s)} ${s.year}`;return s.comp==='wc'?`Rugby League World Cup ${s.year}`:`Test season ${s.year}`}", 'compname')
    js = replace_function(js, 'drawWCPools', DRAW_WC, 'drawwc')
    js = rep(js, "\nfunction ncFixtures(", "\n" + WC_FIX + "\nfunction ncFixtures(")
    # The calendar.
    js = rep(js, "const SIXN_TEAMS=['England','France','Ireland','Italy','Scotland','Wales'],RC_TEAMS=['New Zealand','South Africa','Australia','Argentina'],REC_TEAMS=['Georgia','Romania','Spain','Portugal'],PNC_TEAMS=['Fiji','Japan','Samoa','Tonga','Canada','United States'];",
             "const SIXN_TEAMS=[],RC_TEAMS=[],REC_TEAMS=[],PNC_TEAMS=[];")
    js = line(js, "const INTL_COMPS=", "const INTL_COMPS={pacc:{name:'Pacific Championships',teams:['Australia','New Zealand','Tonga','Samoa'],w:.6},pacc3:{name:'Pacific Championships',teams:['New Zealand','Tonga','Samoa'],w:.6},pacb:{name:'Pacific Bowl',teams:['Papua New Guinea','Fiji','Cook Islands'],w:.4},euro:{name:'European Championship',teams:['France','Wales','Ireland','Scotland'],w:.4},ashes:{name:'The Ashes',teams:['England','Australia'],w:.6},nc:{name:'Nations Championship',w:1},wc:{name:'Rugby League World Cup',w:1},tests:{name:'Tests',w:.25}};", resub, 'intlcomps')
    js = replace_function(js, 'isNCYear', "function isNCYear(y){return false}\nfunction isAshesYear(y){return (y-2025)%4===0}", 'isnc')
    js = replace_function(js, 'yearKind', "function yearKind(y){return isWCYear(y)?'World Cup year':isAshesYear(y)?'Ashes year':'Pacific Championships year'}", 'yearkind')
    js = replace_function(js, 'buildIntlCalendar', CALENDAR, 'calendar')
    js = rep(js, "for(const c of w.comps){if(c==='nc'){", "for(const c of w.comps){if(c==='ashes'){const home=s.year%8===1?'England':'Australia',away=home==='England'?'Australia':'England';for(let i=0;i<3&&i<R;i++)rounds[i].push({a:home,b:away,round:i+1,comp:'ashes'});continue}if(c==='nc'){")
    js = rep(js, "const teams=compTeams(c,s).slice().sort((a,b)=>seeded(a+':'+c+':'+cycle)-seeded(b+':'+c+':'+cycle));rrSlots(teams,w.slots?.[c],R,flip,c,c==='rc'&&!w.single).forEach((r,i)=>rounds[i].push(...r))}",
             "const teams=compTeams(c,s).slice().sort((a,b)=>seeded(a+':'+c+':'+cycle)-seeded(b+':'+c+':'+cycle));rrSlots(teams,w.slots?.[c],R,flip,c,false).forEach((r,i)=>rounds[i].push(...r))}")
    js = rep(js, "if(w.friendlies){const off=w.key==='jul'&&isLionsYear(s.year)?new Set([...HOME_UNIONS,lionsHost(s.year)]):new Set(),need={};", "if(w.friendlies){const off=new Set(),need={};")
    js = rep(js, "if(w.key==='wc'){s.wcHost=wcHost(s.year);s.intlPools=s.year===2027?copy(POOLS):drawWCPools(s);s.fixtures=Array.from({length:3},()=>[]);for(const [poolName,teams] of Object.entries(s.intlPools))rr(teams).forEach((r,i)=>r.forEach(([a,b])=>s.fixtures[i].push({a,b,pool:poolName,round:i+1,comp:'wc',win:'wc'})));s.table=emptyTable(NATIONS)}",
             "if(w.key==='wc'){s.wcHost=wcHost(s.year);s.intlPools=s.year===2026?copy(POOLS):drawWCPools(s);s.fixtures=wcFixtures(s.intlPools).map(r=>r.map(f=>({...f,comp:'wc',win:'wc'})));s.table=emptyTable(NATIONS)}")
    js = rep(js, "log(`${w.name}: no Tests for ${displayTeam(s.team)}${w.key==='jul'&&isLionsYear(s.year)?` while the British & Irish Lions tour ${displayTeam(lionsHost(s.year))}`:''}. Simulate the window to follow the results.`)", "log(`${w.name}: no Tests for ${displayTeam(s.team)}. Simulate the window to follow the results.`)")
    js = rep(js, "if(c==='rc')bledisloeFromRC(s)}", "if(c==='ashes')bledisloeFromRC(s)}")
    js = rep(js, "if(w.key==='jul'&&isLionsYear(s.year))lionsTourNow(s);", "")
    js = replace_function(js, 'migrateIntlSeason', MIGRATE_INTL, 'migrateintl')
    js = replace_function(js, 'setObjective', SET_OBJECTIVE, 'setobjective')
    js = replace_function(js, 'wcStage', WC_STAGE, 'wcstage')
    js = replace_function(js, 'cupKnockout', CUP_KO, 'cupko')
    js = rep(js, "else if(s.phase==='Pools'){if(s.round<2)s.round++;else{s.round=3;cupKnockout()}}", "else if(s.phase==='Pools'){if(s.round<s.fixtures.length-1)s.round++;else{s.round=s.fixtures.length;cupKnockout()}}")
    js = rep(js, "else if(s.phase==='Pools'){s.round++;if(s.round===3)cupKnockout()}", "else if(s.phase==='Pools'){s.round++;if(s.round>=s.fixtures.length)cupKnockout()}")
    js = rep(js, "s.table=emptyTable(NATIONS);s.fixtures=Array.from({length:3},()=>[]);for(const [poolName,teams] of Object.entries(POOLS)){rr(teams).forEach((r,i)=>r.forEach(([a,b])=>s.fixtures[i].push({a,b,pool:poolName,round:i+1})))}",
             "s.table=emptyTable(NATIONS);s.wcHost='Australia';s.fixtures=wcFixtures(POOLS);")
    js = rep(js, "year:mode==='club'?2026:2027,players:copy(DB.players).map(p=>{if(ageOf(p,{year:mode==='club'?2026:2027})<=24)p.potential=Math.max(p.potential,Math.min(93,projectedPeak(p,{year:mode==='club'?2026:2027})));return p})",
             "year:2026,players:copy(DB.players).map(p=>{if(ageOf(p,{year:2026})<=24)p.potential=Math.max(p.potential,Math.min(93,projectedPeak(p,{year:2026})));return p})")
    js = rep(js, "s.year=Math.round(num(s.year,s.mode==='club'?2026:2027));", "s.year=Math.round(num(s.year,2026));")
    js = rep(js, "const valid=c=>c&&[1,2].every(t=>c[t]&&Object.keys(c[t]).length===2&&Object.values(c[t]).every(v=>Array.isArray(v)&&v.length===6))&&NATIONS.every(n=>[1,2].some(t=>Object.values(c[t]).some(v=>v.includes(n))));",
             "const valid=c=>c&&[1,2].every(t=>c[t]&&typeof c[t]==='object')&&NATIONS.every(n=>[1,2].some(t=>Object.values(c[t]).some(v=>Array.isArray(v)&&v.includes(n))));")
    js = rep(js, "function homeEdge(a,b,s){if(!s)return 0;", "function homeEdge(a,b,s){if(!s)return 0;if(s.origin)return a===s.origin.home?2.5:-2.5;")
    js = rep(js, "if(s.career&&s.comp!=='wc'){if(s.phase==='League'||s.phase==='Promotion play-off')return 2+(NAT_REGION[a]===NAT_REGION[b]?.4:1.6);return 0}const h=s.career?s.wcHost:'Australia';return h===a?2.5:h===b?-2.5:0}",
             "if(s.career&&s.comp!=='wc'){if(s.phase==='League'||s.phase==='Promotion play-off')return 2+(NAT_REGION[a]===NAT_REGION[b]?.4:1.6);return 0}const h=s.wcHost||'Australia';return h===a?2.5:h===b?-2.5:0}")
    # World rugby league: the Ashes record; no Lions, no Bledisloe.
    js = replace_function(js, 'bledisloeFromRC', ASHES_FROM_COMP, 'ashes')
    js = replace_function(js, 'isLionsYear', "function isLionsYear(y){return false}", 'islions')
    js = replace_function(js, 'worldRugbyYearTick', WR_TICK, 'wrtick')
    js = replace_function(js, 'worldRugbyHTML', WR_HTML, 'wrhtml')
    js = line(js, "const HOME_UNIONS=", "const HOME_UNIONS=['England','Wales','Ireland','Scotland'];", resub, 'homeunions')
    # Club world cup: the World Club Series, sixteen clubs in four pools.
    js = rep(js, "const CLUB_WORLD_CUP_SIZE=24;", "const CLUB_WORLD_CUP_SIZE=16;")
    js = replace_function(js, 'buildClubPools', "function buildClubPools(qualifiers){const letters=['A','B','C','D'],pools=Object.fromEntries(letters.map(l=>[l,[]]));let idx=0;for(let round=0;round<4;round++){const order=round%2===0?letters:letters.slice().reverse();for(const l of order)if(qualifiers[idx])pools[l].push(qualifiers[idx++])}return pools}", 'clubpools')
    js = rep(js, "function clubSquadForRanking(team){for(const slot of ['club','urc','prem','top14'])", "function clubSquadForRanking(team){for(const slot of ['club','sl'])")
    # State of Origin: three matches through the NRL season. Every Origin player misses the NRL round of his game.
    js = replace_function(js, 'testWindows', TEST_WINDOWS, 'testwindows')
    js = replace_function(js, 'testNations', "function testNations(s,w){return w.origin?['New South Wales','Queensland']:[]}", 'testnations')
    js = replace_function(js, 'testSquad', TEST_SQUAD, 'testsquad')
    js = replace_function(js, 'openWindow', OPEN_WINDOW, 'openwindow')
    js = replace_function(js, 'closeWindow', CLOSE_WINDOW, 'closewindow')
    js = replace_function(js, 'windowCardHTML', WINDOW_CARD, 'windowcard')
    js = rep(js, "// ---------- International Test windows (URC and Premiership seasons) ----------", "// ---------- State of Origin: three matches in the middle of the NRL season ----------")
    # Venues and climate.
    js = rep(js, "const CLIMATE={\n", "const CLIMATE={\n " + CLIMATE_ADD + "\n")
    js = resub(js, r"^const VENUE=\{.*?\n.*?\};", lambda m: VENUE, 1, 'venue', re.M)
    js = rep(js, "const CWC_CITIES=['London','Paris','Sydney','Auckland','Cape Town','Tokyo','Dublin','Buenos Aires'];", "const CWC_CITIES=['Sydney','Brisbane','Leeds','Wigan','Auckland','Perpignan','Melbourne','Hull'];")
    js = rep(js, "return {team:f.a,city:VENUE[f.a]||(NAT_REGION?.[f.a]==='SH'?'Sydney':'London')}}", "if(s&&s.phase==='Grand Final'&&s.mode==='club')return {team:'',city:s.league==='sl'?'Manchester':'Sydney'};return {team:f.a,city:VENUE[f.a]||(NAT_REGION?.[f.a]==='SH'?'Sydney':'London')}}")
    js = rep(js, "if(s.mode==='clubworldcup'||s.cwcActive)return ko?7:6;", "if(s.mode==='clubworldcup'||s.cwcActive)return ko?11:10;")
    js = rep(js, "if(s.mode==='international'){if(s.comp==='wc'||!intlCareer(s))return s.phase==='Pools'?9:10;", "if(s.mode==='international'){if(s.comp==='wc'||!intlCareer(s))return s.phase==='Pools'?10:11;")
    js = rep(js, "const L=s.league||'super',rounds=Math.max(1,s.fixtures?.length||16);if(L==='super')return ko?6:2+Math.min(3,Math.floor(r*4/rounds));return ko?6:(8+Math.floor(r*9/rounds))%12+1}",
             "const L=s.league||'nrl',rounds=Math.max(1,s.fixtures?.length||27);if(L==='nrl')return ko?9:3+Math.min(5,Math.floor(r*6/rounds));return ko?10:2+Math.min(7,Math.floor(r*8/rounds))}")
    js = rep(js, "X.altF=wx.alt>1000&&!(['Bulls','Lions','South Africa','Zimbabwe'].includes(X.team))&&home!==hostReg?1.08:1", "X.altF=wx.alt>1000&&!(['Papua New Guinea'].includes(X.team))&&home!==hostReg?1.08:1")
    js = rep(js, "const ROOF_RETRACT={Wales:1};", "const ROOF_RETRACT={};")
    return js

DRAW_WC = r"""function drawWCPools(s){const lad=natLadder(s).map(r=>r.team),host=wcHost(s.year),field=lad.slice(0,10);if(!field.includes(host)){field.pop();field.push(host)}const r=field.slice().sort((a,b)=>lad.indexOf(a)-lad.indexOf(b));return {A:[r[0],r[1],r[8],r[9]],B:[r[2],r[5],r[6]],C:[r[3],r[4],r[7]]}}"""

WC_FIX = r"""// The 2026 format: Group A plays a round robin; Groups B and C play each other, three matches each, on one combined table.
function wcFixtures(pools){const rounds=[[],[],[]],P=pools||POOLS;if(P.B&&P.C&&P.B.length===3&&P.C.length===3&&!P.D){rr(P.A).forEach((r,i)=>r.forEach(([a,b])=>rounds[i].push({a,b,pool:'A',round:i+1})));for(let i=0;i<3;i++)for(let j=0;j<3;j++){const b=P.B[j],c=P.C[(j+i)%3],home=(i+j)%2===0;rounds[i].push({a:home?b:c,b:home?c:b,pool:'B/C',round:i+1})}return rounds}
 for(const [pn,teams] of Object.entries(P))rr(teams).forEach((r,i)=>r.forEach(([a,b])=>rounds[i].push({a,b,pool:pn,round:i+1})));return rounds}
function wcGroups(pools){const P=pools||POOLS;return P.B&&P.C&&P.B.length===3&&P.C.length===3&&!P.D?{'A':P.A,'B & C':[...P.B,...P.C]}:P}"""

CALENDAR = r"""function buildIntlCalendar(y){const wc=isWCYear(y),ashes=isAshesYear(y),W=[{key:'mid',name:'Mid-season Tests',when:'June',months:[6],rounds:1,comps:[],friendlies:1,tests:'Mid-season Tests'}];
 if(wc)W.push({key:'wc',name:'Rugby League World Cup',when:'Oct – Nov',months:[10,10,10,11,11],comps:['wc']});
 else W.push({key:'end',name:ashes?'The Ashes & Pacific Championships':'Pacific Championships & end-of-year Tests',when:'Oct – Nov',months:[10,10,11],rounds:3,comps:ashes?['ashes','pacc3','pacb','euro']:['pacc','pacb','euro'],friendlies:2,tests:'End-of-year Tests'});
 return W}"""

MIGRATE_INTL = r"""function migrateIntlSeason(s){const keys=['mid','end','wc'];if(!Array.isArray(s.cal)||!s.cal.length||!s.cal.every(w=>w&&typeof w==='object'&&keys.includes(w.key)&&Array.isArray(w.comps))){s.cal=buildIntlCalendar(s.year);s.calIdx=Math.min(s.cal.length-1,Math.max(0,Number(s.calIdx)||0))}
 s.calIdx=clamp(Math.round(Number(s.calIdx)||0),0,s.cal.length-1);s.comp=s.cal[s.calIdx].key;if(!s.tables||typeof s.tables!=='object')s.tables={};if(!Array.isArray(s.yearLog))s.yearLog=[];if(!Array.isArray(s.squadSwaps))s.squadSwaps=[];if(s.objective&&typeof s.objective==='object'&&!s.objective.comp)s.objective.comp=s.objective.kind}"""

SET_OBJECTIVE = r"""function setObjective(s){const rk=natRankPos(s,s.team),w=curWin(s),c=w?winCompOf(s.team,w,s):(s.comp==='wc'?'wc':'tests');
 if(c==='wc'){const inWC=Object.values(s.intlPools||{}).flat().includes(s.team);if(!inWC){s.objective={kind:'none',comp:'wc',need:0,text:'Not at this World Cup'};return}const need=rk<=2?4:rk<=5?2:0;s.objective={kind:'wc',comp:'wc',need,text:{0:'Win at least one group match',2:'Reach the semi-finals',4:'Reach the final'}[need]};return}
 if(c==='tests'){const g=(s.fixtures||[]).flat().filter(f=>f.a===s.team||f.b===s.team);if(!g.length){s.objective={kind:'none',comp:'tests',need:0,text:'No Tests for your side in this window'};return}const R=ensureNatRank(s),exp=g.reduce((k,f)=>{const home=f.a===s.team,d=R[s.team]-R[home?f.b:f.a]+(home?3:-3);return k+1/(1+Math.exp(-d/4))},0),need=clamp(Math.floor(exp+.25),1,g.length);s.objective={kind:'tests',comp:'tests',need,text:need===g.length?`Win all ${g.length} of your ${w.tests}`:`Win at least ${need} of your ${g.length} ${w.tests}`};return}
 if(c==='ashes'){const R=ensureNatRank(s),opp=s.team==='England'?'Australia':'England',fav=R[s.team]>=R[opp];s.objective={kind:'tests',comp:'ashes',need:fav?2:1,text:fav?'Win the Ashes series':'Win at least one Ashes Test'};return}
 const teams=compTeams(c,s),n=teams.length,inComp=natLadder(s).filter(r=>teams.includes(r.team)).findIndex(r=>r.team===s.team)+1,need=inComp<=1?1:inComp<=2?2:n-1,name=INTL_COMPS[c].name;
 s.objective={kind:'league',comp:c,need,text:need>=n-1?`Avoid finishing bottom of the ${name}`:need===1?`Win the ${name}`:`Finish in the top two of the ${name}`}}"""

WC_STAGE = r"""function wcStage(s){let lvl=0,label='Out in the group stage';for(const st of s.knockouts||[]){const r=st.reports.find(x=>x.a===s.team||x.b===s.team);if(!r)continue;if(st.stage==='Quarter-finals'){lvl=Math.max(lvl,1);label='Quarter-finalists'}else if(st.stage==='Semi-finals'){lvl=Math.max(lvl,2);label='Semi-finalists'}else if(st.stage==='Final'||st.stage==='Finals'){lvl=r.winner===s.team?5:4;label=r.winner===s.team?'World champions':'Runners-up'}}const poolWins=s.results.filter(r=>r.year===s.year&&r.phase==='Pools'&&r.winner===s.team).length;return {lvl,label,poolWins}}"""

CUP_KO = r"""function cupKnockout(){const s=game(),pools=poolsFor(s),groups=wcGroups(pools),order={};for(const [g,ts] of Object.entries(groups))order[g]=standings(ts);const keys=Object.keys(order);
 if(keys.length===2){const [A,B]=keys;s.pending=[{a:order[A][0].name,b:order[B][1].name},{a:order[B][0].name,b:order[A][1].name}];s.phase='Semi-finals';s.seeds=[order[A][0].name,order[B][0].name,order[A][1].name,order[B][1].name];log(`The group stage is over. Semi-finals: ${s.pending.map(f=>`${displayTeam(f.a)} v ${displayTeam(f.b)}`).join(', ')}.`);return}
 const L=keys;s.pending=[];for(let i=0;i<L.length;i+=2){const a=order[L[i]],b=order[L[i+1]||L[0]];s.pending.push({a:a[0].name,b:b[1].name},{a:b[0].name,b:a[1].name})}s.seeds=s.pending.flatMap(f=>[f.a,f.b]);s.phase='Quarter-finals';log('Pool stage complete. The top two in each pool go through to the quarter-finals.')}"""

ASHES_FROM_COMP = r"""function bledisloeFromRC(s){const g=s.results.filter(r=>r.year===s.year&&r.comp==='ashes'),wr=ensureWorldRugby(s),b=wr.bledisloe;if(!g.length||b.lastYear===s.year)return;let ew=0,aw=0;const tests=g.map(r=>{const e=r.a==='England'?r.x:r.y,a=r.a==='Australia'?r.x:r.y;if(e>a)ew++;else if(a>e)aw++;return {aus:a,nz:e}});
 const winner=aw>ew?'Australia':ew>aw?'England':b.holder||'Australia';if(winner!==b.holder){b.holder=winner;b.streak=1}else b.streak=(b.streak||0)+1;b.lastYear=s.year;b.log=[{year:s.year,holder:winner,tests},...b.log].slice(0,20);
 if(s.team==='Australia'||s.team==='England')log(winner===s.team?`${displayTeam(s.team)} ${b.streak>1?'retain':'win'} the Ashes.`:`${displayTeam(winner)} hold the Ashes.`)}"""

WR_TICK = r"""function worldRugbyYearTick(s,year){const wr=ensureWorldRugby(s);if(!isAshesYear(year)||wr.bledisloe.lastYear===year)return;const b=wr.bledisloe;let ew=0,aw=0;const tests=[0,1,2].map(()=>{const r=simpleTestResult('Australia','England',s);if(r.x>r.y)aw++;else if(r.y>r.x)ew++;return {aus:r.x,nz:r.y}}),winner=aw>ew?'Australia':ew>aw?'England':b.holder||'Australia';if(winner!==b.holder){b.holder=winner;b.streak=1}else b.streak=(b.streak||0)+1;b.lastYear=year;b.log=[{year,holder:winner,tests},...b.log].slice(0,20);inboxNote?.(s,'news',`${winner} ${b.streak>1?'retain':'win'} the Ashes`,`${winner} take the Ashes series ${Math.max(aw,ew)}-${Math.min(aw,ew)}.`)}"""

WR_HTML = r"""function worldRugbyHTML(s){const wr=ensureWorldRugby(s),b=wr.bledisloe;
 return `<section class="card" style="margin-top:16px"><h2>The Ashes</h2><p class="sub muted hint">England and Australia, a three-Test series every four years. A drawn series leaves the Ashes with the holder.</p>${b.holder?`<div class="row"><span>Holder</span><b>${esc(displayTeam(b.holder))} <span class="tiny muted">${b.streak} series running</span></b></div>${b.log.slice(0,6).map(l=>`<div class="row"><span class="sub">${l.year}</span><b>Australia ${l.tests?l.tests.map(t=>`${t.aus}–${t.nz}`).join(', '):''} England</b></div>`).join('')}`:'<div class="empty">Not yet contested in this save.</div>'}</section>`}"""

TEST_WINDOWS = r"""function testWindows(s){if(!s||s.mode!=='club'||s.cwcActive||s.league!=='nrl')return [];const n=(s.fixtures||[]).length;if(n<15)return [];return [{key:'o1',name:'State of Origin · Game I',start:Math.round(n*.45),len:1,origin:1},{key:'o2',name:'State of Origin · Game II',start:Math.round(n*.55),len:1,origin:2},{key:'o3',name:'State of Origin · Game III',start:Math.round(n*.66),len:1,origin:3}]}"""

TEST_SQUAD = r"""function testSquad(s,state){const code=state==='Queensland'?'QLD':'NSW',cands=s.players.filter(p=>p.origin===code&&p.nation==='Australia'&&!p.retired&&p.club&&LEAGUES.nrl.teams.includes(p.club)&&!(p.injuryRounds>0)&&!p.suspendedRounds).sort((a,b)=>effective(b)-effective(a)),out=[],q={PR:3,HK:2,SR:3,LK:1,HB:1,FE:1,CE:2,OB:3};for(const p of cands){if(q[p.pos]>0){q[p.pos]--;out.push(p)}if(out.length>=SQ17)break}for(const p of cands){if(out.length>=SQ17)break;if(!out.includes(p))out.push(p)}return out}"""

OPEN_WINDOW = r"""function openWindow(s,w){const mine=[],sides={};for(const n of testNations(s,w)){sides[n]=testSquad(s,n);for(const p of sides[n]){if(p.pro)continue;p.intlDuty=n;if(p.club===s.team)mine.push(p)}}s.window={key:w.key,name:w.name,year:s.year,start:w.start,end:w.start+w.len,origin:w.origin};
 if(Array.isArray(s.lineup))s.lineup=s.lineup.map(id=>{const p=player(id);return p&&p.intlDuty?null:id});
 if(w.origin){const O=s.originSeries&&s.originSeries.year===s.year?s.originSeries:(s.originSeries={year:s.year,games:[]}),str=n=>top23Avg(sides[n]||[]),home=w.origin===2?'Queensland':'New South Wales',d=str('New South Wales')-str('Queensland')+(home==='New South Wales'?2:-2),base=18+gauss()*4,nsw=Math.max(0,Math.round(base+d*.6+gauss()*7)),qld=Math.max(0,Math.round(base-d*.6+gauss()*7));let N=nsw,Q=qld;if(N===Q){if(Math.random()<.5+d*.03)N++;else Q++}O.games.push({g:w.origin,nsw:N,qld:Q,home});const nw=O.games.filter(g=>g.nsw>g.qld).length,qw=O.games.filter(g=>g.qld>g.nsw).length;if(nw>=2||qw>=2)O.winner=nw>qw?'New South Wales':'Queensland';
  for(const n of Object.keys(sides))for(const p of sides[n]){p.og=(p.og||0)+1}
  log(`${w.name}: ${N>Q?'New South Wales':'Queensland'} win ${Math.max(N,Q)}–${Math.min(N,Q)}${home?` in ${home==='New South Wales'?'Sydney':'Brisbane'}`:''}.${O.winner&&!O.told?` ${O.winner} win the series.`:''}${mine.length?` Your Origin players miss this round: ${mine.map(p=>`${p.name} (${p.intlDuty==='Queensland'?'QLD':'NSW'})`).join(', ')}.`:' None of your players were picked.'}`);if(O.winner&&!O.told){O.told=1;addNews?.(s,'move',`${O.winner} win the State of Origin series ${Math.max(nw,qw)}–${Math.min(nw,qw)}.`)}}
 else log(mine.length?`${w.name}: ${mine.length} of your players are called up.`:`${w.name}: none of your players are called up.`)}"""

CLOSE_WINDOW = r"""function closeWindow(s){if(!s||!s.window)return;const back=[],key=s.window.key,name=s.window.name;for(const p of s.players){if(!p.intlDuty)continue;p.intlDuty=null;p.fitness=Math.min(p.fitness,84);if(seeded(p.id+':origin:'+s.year+key)<.05)injure(p,ageOf(p,s),p.club);if(p.club===s.team)back.push(p.name)}
 for(const p of s.players)if(p.windowCover===key&&p.club&&p.club!==s.team){p.club='';p.years=0;p.faYears=0;p.windowCover=null}
 if(back.length)log(`${name} over: ${back.join(', ')} ${back.length===1?'is':'are'} back for club duty.`);s.window=null}"""

WINDOW_CARD = r"""function windowCardHTML(s){const ws=testWindows(s);if(!ws.length||s.phase!=='League')return '';const O=s.originSeries&&s.originSeries.year===s.year?s.originSeries:null,series=O&&O.games.length?`<p class="tiny muted">Series so far: ${O.games.map(g=>`Game ${['','I','II','III'][g.g]} NSW ${g.nsw}–${g.qld} QLD`).join(' · ')}${O.winner?` · <b>${esc(O.winner)} win the series</b>`:''}</p>`:'';
 if(s.window){const away=pool(s.team).filter(p=>p.intlDuty);return `<section class="card window-card"><div class="eyebrow">${esc(s.window.name)}</div><h2>${away.length} player${away.length===1?'':'s'} on Origin duty</h2><p class="sub muted">They miss this round. ${away.length?'Your depth is being tested; your first-choice 17 is covered automatically.':'Your whole squad is available.'}</p>${away.length?`<div class="md-strip">${away.map(p=>`<span class="tag cover">${esc(p.name)} · ${p.intlDuty==='Queensland'?'QLD':'NSW'}</span>`).join('')}</div>`:''}${series}</section>`}
 const next=ws.find(w=>s.round<w.start&&w.start-s.round<=3);if(!next)return O&&O.games.length?`<section class="card window-card"><div class="eyebrow">State of Origin ${s.year}</div>${series}</section>`:'';const likely=testNations(s,next).flatMap(n=>testSquad(s,n)).filter(p=>p.club===s.team),k=next.start-s.round;return `<section class="card window-card"><div class="eyebrow">Coming up · ${esc(next.name)}</div><h2>${k===1?'After this round':`In ${k} rounds`}: round ${next.start+1}</h2><p class="sub muted">The Origin selectors are likely to pick ${likely.length} of your players, and they will miss that NRL round. Plan your depth now.</p>${likely.length?`<div class="md-strip">${likely.map(p=>`<span class="tag">${esc(p.name)} · ${p.origin}</span>`).join('')}</div>`:''}${series}</section>`}"""

CLIMATE_ADD = r"""'Gold Coast':{t:22,a:4,hot:1,r:.25,ra:.12,wet:2,w:14,h:.7},Townsville:{t:25,a:4,hot:1,r:.22,ra:.25,wet:2,w:16,h:.7},Melbourne:{t:15,a:5,hot:1,r:.3,ra:.06,wet:8,w:18,h:.65,roof:'closed'},Wollongong:{t:18,a:4.5,hot:1,r:.3,ra:.06,wet:6,w:18,h:.68},'Newcastle NSW':{t:18.5,a:4.5,hot:1,r:.3,ra:.06,wet:6,w:18,h:.68},Redcliffe:{t:21,a:5,hot:1,r:.25,ra:.12,wet:1,w:14,h:.7},Campbelltown:{t:17,a:6,hot:1,r:.25,ra:.05,wet:6,w:12,h:.6},
 Bradford:{t:9.5,a:6,hot:7,r:.45,ra:.08,wet:12,w:18,h:.82},Castleford:{t:10,a:6,hot:7,r:.4,ra:.06,wet:12,w:16,h:.8},Huddersfield:{t:9.5,a:6,hot:7,r:.48,ra:.08,wet:12,w:18,h:.83},Hull:{t:10,a:6,hot:7,r:.38,ra:.05,wet:11,w:20,h:.8},Leeds:{t:10,a:6,hot:7,r:.4,ra:.06,wet:12,w:16,h:.8},Leigh:{t:10,a:6,hot:7,r:.48,ra:.08,wet:12,w:16,h:.82},'St Helens':{t:10,a:6,hot:7,r:.48,ra:.08,wet:12,w:18,h:.82},Wakefield:{t:10,a:6,hot:7,r:.4,ra:.06,wet:12,w:16,h:.8},Warrington:{t:10.5,a:6,hot:7,r:.46,ra:.08,wet:12,w:16,h:.82},Wigan:{t:10,a:6,hot:7,r:.5,ra:.08,wet:12,w:16,h:.83},York:{t:10,a:6,hot:7,r:.36,ra:.05,wet:11,w:15,h:.8},
 'Port Moresby':{t:27,a:1,hot:12,r:.3,ra:.25,wet:2,w:12,h:.75},Rarotonga:{t:24,a:2.5,hot:2,r:.35,ra:.12,wet:2,w:16,h:.8},Beirut:{t:21,a:6,hot:8,r:.15,ra:.15,wet:1,w:12,h:.66},"""

VENUE = r"""const VENUE={'Brisbane Broncos':'Brisbane','Canberra Raiders':'Canberra','Canterbury-Bankstown Bulldogs':'Sydney','Cronulla-Sutherland Sharks':'Sydney','Dolphins':'Redcliffe','Gold Coast Titans':'Gold Coast','Manly Warringah Sea Eagles':'Sydney','Melbourne Storm':'Melbourne','Newcastle Knights':'Newcastle NSW','North Queensland Cowboys':'Townsville','Parramatta Eels':'Sydney','Penrith Panthers':'Sydney','South Sydney Rabbitohs':'Sydney','St George Illawarra Dragons':'Wollongong','Sydney Roosters':'Sydney','New Zealand Warriors':'Auckland','Wests Tigers':'Campbelltown','Bradford Bulls':'Bradford','Castleford Tigers':'Castleford','Catalans Dragons':'Perpignan','Huddersfield Giants':'Huddersfield','Hull FC':'Hull','Hull Kingston Rovers':'Hull','Leeds Rhinos':'Leeds','Leigh Leopards':'Leigh','St Helens':'St Helens','Toulouse Olympique':'Toulouse','Wakefield Trinity':'Wakefield','Warrington Wolves':'Warrington','Wigan Warriors':'Wigan','York Knights':'York',
 Australia:'Sydney','New Zealand':'Auckland',England:'London',Tonga:'Nukualofa',Samoa:'Apia','Papua New Guinea':'Port Moresby',Fiji:'Suva','Cook Islands':'Rarotonga',France:'Perpignan',Lebanon:'Beirut',Wales:'Cardiff',Ireland:'Dublin',Scotland:'Edinburgh',Italy:'Rome','New South Wales':'Sydney',Queensland:'Brisbane'};"""
