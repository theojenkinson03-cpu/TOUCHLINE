"""Every remaining table keyed by union position groups, now keyed by league groups."""

def apply(js, rep, resub, replace_function):
    js = rep(js, "const Q={PR:6,HK:3,LK:4,BR:6,SH:3,FH:3,CE:4,OB:6},out=[];", "const Q={PR:5,HK:3,SR:5,LK:3,HB:3,FE:3,CE:4,OB:6},out=[];")
    js = rep(js, "proDraft={name:'',nation:'New Zealand',pos:'FH',role:'FH',", "proDraft={name:'',nation:'Australia',pos:'HB',role:'HB',")
    js = rep(js, "const PRO_POS=[['PR','Prop'],['HK','Hooker'],['LK','Lock'],['BR','Back row'],['SH','Scrum-half'],['FH','Fly-half'],['CE','Centre'],['OB','Back three']];", "const PRO_POS=[['PR','Prop'],['HK','Hooker'],['SR','Second row'],['LK','Lock'],['HB','Halfback'],['FE','Five-eighth'],['CE','Centre'],['OB','Wing or fullback']];")
    js = rep(js, "const PRO_ROLE_N={LHP:'Loosehead prop',THP:'Tighthead prop',HK:'Hooker',LK:'Lock',BF:'Blindside flanker',OF:'Openside flanker',N8:'Number eight',SH:'Scrum-half',FH:'Fly-half',IC:'Inside centre',OC:'Outside centre',WG:'Wing',FB:'Full-back'};", "const PRO_ROLE_N={PR:'Prop',HK:'Hooker',SR:'Second row',LK:'Lock',HB:'Halfback',FE:'Five-eighth',CE:'Centre',WG:'Wing',FB:'Fullback'};")
    js = rep(js, "const PRO_FOCUS={attack:'Attack',defence:'Defence',pace:'Pace',kicking:'Kicking',setpiece:'Set piece',discipline:'Discipline'};", "const PRO_FOCUS={attack:'Attack',defence:'Defence',pace:'Pace',kicking:'Kicking',setpiece:'Power',discipline:'Discipline'};")
    js = replace_function(js, 'proFocusFor', "function proFocusFor(pos){return ({PR:'setpiece',HK:'attack',SR:'defence',LK:'defence',HB:'kicking',FE:'attack',CE:'attack',OB:'pace'})[pos]||'attack'}", 'profocus')
    js = replace_function(js, 'proStartersN', "function proStartersN(pos){return {PR:2,HK:1,SR:2,LK:1,HB:1,FE:1,CE:2,OB:3}[pos]||2}", 'starters')
    js = replace_function(js, 'proBenchN', "function proBenchN(pos){return {PR:2,HK:1,SR:1,LK:0,HB:0,FE:0,CE:0,OB:0}[pos]||0}", 'bench')
    js = rep(js, "me.role=ROLE_GROUP[d.role]===d.pos?d.role:(GROUP_ROLES[d.pos]||['BF'])[0];", "me.role=ROLE_GROUP[d.role]===d.pos?d.role:(GROUP_ROLES[d.pos]||['SR'])[0];")
    js = rep(js, "const fw=['PR','HK','LK','BR'].includes(me.pos),sub=X.bench.find(b=>player(b)?.pos===me.pos)||X.bench.find(b=>['PR','HK','LK','BR'].includes(player(b)?.pos)===fw);",
             "const fw=['PR','HK','SR','LK'].includes(me.pos),sub=X.bench.find(b=>player(b)?.pos===me.pos)||X.bench.find(b=>['PR','HK','SR','LK'].includes(player(b)?.pos)===fw);")
    js = replace_function(js, 'proForward', "function proForward(M){return ['PR','HK','SR','LK'].includes(proMe(M)?.pos)}", 'proforward')
    js = replace_function(js, 'proCoverP0', "function proCoverP0(M){const pos=proMe(M)?.pos;return pos==='OB'?.4:['CE','FE','HB'].includes(pos)?.3:pos==='SR'?.24:pos==='LK'?.18:.12}", 'cover0')
    js = replace_function(js, 'proRuckP0', "function proRuckP0(M,possF){const pos=proMe(M)?.pos;return (pos==='LK'?.034:pos==='SR'?.03:pos==='HK'?.026:pos==='PR'?.024:pos==='CE'?.014:pos==='HB'?.01:.008)*possF}", 'ruck0')
    js = replace_function(js, 'proMate', "function proMate(X,id){return [1,4,2,3,0,10,11].map(i=>X.on[i]).find(x=>x&&x!==id)||X.on.find(x=>x&&x!==id)}", 'mate')
    js = replace_function(js, 'proBreakP0', "function proBreakP0(M){const p=proMe(M),pos=p?.pos;return pos==='OB'||roleOf(p)==='FB'?.15:pos==='CE'?.15:pos==='FE'?.14:pos==='HB'?.1:pos==='SR'?.1:pos==='LK'||pos==='HK'?.05:.03}", 'break0')
    js = rep(js, "slots=me.pos==='BR'||me.pos==='OB'?3:['PR','LK','CE'].includes(me.pos)?2:1", "slots=me.pos==='OB'?3:['PR','SR','CE'].includes(me.pos)?2:1")
    js = rep(js, "if(me.kickFirst||me.pos==='FH')objs.push({k:'kick',n:'Kick 75% at goal (5 kicks or more)',t:.75});else if(['PR','HK','LK','BR'].includes(me.pos))objs.push({k:'to',n:'Win 6 turnovers',t:6});",
             "if(me.kickFirst||me.pos==='HB')objs.push({k:'kick',n:'Kick 75% at goal (5 kicks or more)',t:.75});else if(['PR','HK','SR','LK'].includes(me.pos))objs.push({k:'tk',n:regular?'Make 350 tackles':'Make 150 tackles',t:regular?350:150});")
    js = rep(js, "if(o.k==='to')return se.turnovers||0;", "if(o.k==='to')return se.turnovers||0;if(o.k==='tk')return se.tackles||0;")
    js = rep(js, "num={PR:'1 and 3',HK:'2',LK:'4 and 5',BR:'6, 7 and 8',SH:'9',FH:'10',CE:'12 and 13',OB:'11, 14 and 15'}[me.pos]||''", "num={PR:'8 and 10',HK:'9',SR:'11 and 12',LK:'13',HB:'7',FE:'6',CE:'3 and 4',OB:'1, 2 and 5'}[me.pos]||''")
    js = rep(js, "const alt=({LHP:'THP',THP:'LHP',BF:'OF',OF:'N8',N8:'BF',IC:'OC',OC:'IC',WG:'FB',FB:'WG',SH:'WG',FH:'IC',LK:'BF',HK:'LHP'})[me.role];", "const alt=({PR:'LK',LK:'SR',SR:'LK',HK:'HB',HB:'FE',FE:'HB',CE:'WG',WG:'FB',FB:'WG'})[me.role];")
    js = rep(js, "req={PR:5,HK:3,LK:3,BR:4,SH:2,FH:2,CE:3,OB:4}[p.pos]||3", "req={PR:5,HK:2,SR:4,LK:2,HB:2,FE:2,CE:3,OB:5}[p.pos]||3")
    js = rep(js, "req={PR:5,HK:3,LK:3,BR:4,SH:2,FH:2,CE:3,OB:4};", "req={PR:5,HK:2,SR:4,LK:2,HB:2,FE:2,CE:3,OB:5};")
    js = rep(js, "const WINDOW_QUOTA={PR:5,HK:3,LK:4,BR:6,SH:3,FH:2,CE:4,OB:6};", "const WINDOW_QUOTA={PR:4,HK:2,SR:4,LK:2,HB:2,FE:2,CE:3,OB:5};")
    js = rep(js, "const DEPTH_NEED={PR:4,HK:2,LK:3,BR:4,SH:2,FH:1,CE:2,OB:3};", "const DEPTH_NEED={PR:4,HK:2,SR:3,LK:2,HB:1,FE:1,CE:3,OB:4};")
    js = rep(js, "const GROUP_STARTERS={PR:2,HK:1,LK:2,BR:3,SH:1,FH:1,CE:2,OB:3};", "const GROUP_STARTERS={PR:2,HK:1,SR:2,LK:1,HB:1,FE:1,CE:2,OB:3};")
    js = rep(js, "const PLAN_NEED={PR:6,HK:3,LK:4,BR:6,SH:3,FH:2,CE:4,OB:6};", "const PLAN_NEED={PR:5,HK:2,SR:4,LK:3,HB:2,FE:2,CE:4,OB:6};")
    js = rep(js, "function proPickBonus(s){return p=>p.pro?(s.pro.trust-50)/7:0}", "function proPickBonus(s){return p=>p.pro?(s.pro.trust-50)/7:0}")
    return js
