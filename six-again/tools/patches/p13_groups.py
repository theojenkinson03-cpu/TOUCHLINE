"""World Cup groups on screen: Group A, and Groups B & C on one table."""

def apply(js, rep, resub, replace_function):
    js = rep(js, "\nfunction ncFixtures(", "\n" + HELPERS + "\nfunction ncFixtures(")
    js = rep(js, "const pos=standings(poolsFor(s)[poolOf(s.team,s)]).findIndex(t=>t.name===s.team)+1;return `Currently ${ordinal(pos)} in Pool ${poolOf(s.team,s)}. The top two and the four best third-placed teams go through.`}",
             "const g=groupOf(s.team,s),pos=standings(g.teams).findIndex(t=>t.name===s.team)+1;return `Currently ${ordinal(pos)} in ${g.label}. The top two go through to the ${s.mode==='international'?'semi-finals':'quarter-finals'}.`}")
    js = rep(js, "s.phase==='Pools'?`Pool ${poolOf(s.team,s)} · matchday ${s.round+1} of 3`", "s.phase==='Pools'?`${groupOf(s.team,s).label} · matchday ${s.round+1} of ${(s.fixtures||[]).length||3}`")
    js = rep(js, "const p=Object.entries(W.pools).find(([,t])=>t.includes(N));if(p){const o=tSort(W.table,p[1]);return `Pool ${p[0]}: ${ordinal(o.findIndex(r=>r.name===N)+1)}`}", "const p=Object.entries(wcGroups(W.pools)).find(([,t])=>t.includes(N));if(p){const o=tSort(W.table,p[1]);return `${p[0].length>1?'Groups':'Group'} ${p[0]}: ${ordinal(o.findIndex(r=>r.name===N)+1)}`}")
    js = rep(js, "const mine=Object.entries(W.pools).find(([,t])=>t.includes(N));title='Rugby League World Cup';body=`${mine?`<h3 style=\"margin:0 0 6px\">Pool ${mine[0]}</h3>", "const mine=Object.entries(wcGroups(W.pools)).find(([,t])=>t.includes(N));title='Rugby League World Cup';body=`${mine?`<h3 style=\"margin:0 0 6px\">${mine[0].length>1?'Groups':'Group'} ${mine[0]}</h3>")
    js = rep(js, ":'World Cup · Pool '+poolOf(s.team)}", ":'World Cup · '+groupOf(s.team,s).label}")
    js = rep(js, "`<div class=\"two\">${Object.entries(poolsFor(s)).map(([k,teams])=>`<section class=\"card\"><h3>POOL ${k}</h3>${tableHTML(teams,true)}</section>`).join('')}</div>`", "`<div class=\"two\">${Object.entries(s.mode==='international'?wcGroups(poolsFor(s)):poolsFor(s)).map(([k,teams])=>`<section class=\"card\"><h3>${s.mode==='international'?(k.length>1?'GROUPS ':'GROUP '):'POOL '}${k}</h3>${tableHTML(teams,true)}</section>`).join('')}</div>`")
    js = rep(js, "${r.pool?' · Pool '+esc(r.pool):''}", "${r.pool?(r.cwc||!/\\//.test(r.pool)&&!r.comp&&s.mode!=='international'?' · Pool ':' · Group ')+esc(r.pool.replace('/',' & ')):''}")
    js = rep(js, "if(f.pool)return `Pool ${f.pool} · matchday ${f.round}`;", "if(f.pool)return `${f.comp==='wc'?'Group':'Pool'} ${f.pool.replace('/',' & ')} · matchday ${f.round}`;")
    js = rep(js, "s.objective={kind:'tests',comp:'tests',need,text:need===g.length?`Win all ${g.length} of your ${w.tests}`:`Win at least ${need} of your ${g.length} ${w.tests}`};return}",
             "s.objective={kind:'tests',comp:'tests',need,text:g.length===1?`Win your ${w.tests.replace(/s$/,'')}`:need===g.length?`Win all ${g.length} of your ${w.tests}`:`Win at least ${need} of your ${g.length} ${w.tests}`};return}")
    return js

HELPERS = r"""function groupOf(team,s=game()){const P=poolsFor(s)||{},G=s&&s.mode==='international'?wcGroups(P):P,k=Object.keys(G).find(x=>G[x].includes(team));return {key:k,teams:k?G[k]:[team],label:k?(s&&s.mode==='international'?(k.length>1?`Groups ${k}`:`Group ${k}`):`Pool ${k}`):''}}"""
