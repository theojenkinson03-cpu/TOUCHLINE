"""Penalty kicks for touch in league terms, and the second sweep of on-screen text."""
import re

def apply(js, rep, resub, replace_function):
    js = rep(js, "const TOUCH_Z=[[1,'try'],[6,'impact'],[22,'standard']]", "const TOUCH_Z=[[1,'try'],[6,'impact'],[20,'standard']]")
    js = rep(js, "const lines=[22,40].filter(", "const lines=[20,40].filter(")
    js = rep(js, "Z=[[v.y0,0,'#ff8a7a','LOST BALL'],[b[0],b[1],'#f2c14e','TRY'],[b[1],b[2],'#7ee08a','IMPACT'],[b[2],b[3],'#8fc3ff','STANDARD'],[b[3],yEnd,'#ff8a7a','LOST BALL']]", "Z=[[v.y0,0,'#ff8a7a','DEAD'],[b[0],b[1],'#f2c14e','ON THE LINE'],[b[1],b[2],'#7ee08a','IMPACT'],[b[2],b[3],'#8fc3ff','IN THEIR 20'],[b[3],yEnd,'#ffb36b','FAR OUT']]")
    js = replace_function(js, 'touchResolve', TOUCH_RESOLVE, 'touchresolve')
    js = rep(js, "standard:`Out ${mm(ko.y)} from their line: a standard line-out.`,short:`Out ${mm(ko.y)} from their line: lost ball.`", "standard:`Out ${mm(ko.y)} from their line: a fresh set inside their 20.`,short:`Out ${mm(ko.y)} from their line: a fresh set, but a long way out.`")
    js = resub(js, r"Attack, pace and kicking decide your moments with the ball; defence your tackles and breakdown work; set piece your scrums, line-outs and pick-and-go; discipline how often you give away penalties\.", "Attack, pace and kicking decide your moments with the ball; defence your tackles and ruck work; power your carries, your play-the-ball speed and your strength in the tackle; discipline how often you give away penalties and six agains.", 1, 'focus')
    js = rep(js, "Match ratings judge tackles, metres, line breaks, turnovers, set piece, goal kicking, tries and assists", "Match ratings judge tackles, metres, line breaks, errors forced, ruck speed, goal kicking, tries and try assists")
    js = rep(js, "The pool draw is complete.", "The draw is complete.")
    js = rep(js, "log('Pool stage complete. The top two in each pool go through to the quarter-finals.')", "log('The pool stage is over. The top two in each pool go through to the quarter-finals.')")
    js = resub(js, r"'The selectors name a squad for every window: the Six Nations or the Rugby Championship, the Nations Championship in even years, tours and Tests, and the World Cup every four years\.", "'The selectors name a squad for every window: the mid-season Tests, the Pacific Championships, the European Championship or the Ashes, and the World Cup every four years.", 1, 'protest')
    js = resub(js, r"\['bonus10','Bonus hunters','Earn ten bonus points in one season\.'\]", "['bonus10','Golden point heroes','Win two golden-point matches in one season.']", 1, 'ach-bonus')
    js = resub(js, r"\['fourteen','Fourteen heroes','Win after one of your players is sent o", "['fourteen','Twelve heroes','Win after one of your players is sent o", 1, 'ach-14')
    # Results meta: no bonus points in league.
    js = replace_function(js, 'bonusOf', "function bonusOf(s,r,team){return 0}", 'bonusof')
    js = rep(js, "Ratings move after every match: up to three points either way,", "Ratings move after every match: up to three rating points either way,")
    return js

TOUCH_RESOLVE = r"""function touchResolve(M,C,c){const X=M.t[C.side],Y=M.t[C.opp],m=C.m,me=proMe(M),aim=c&&typeof c==='object'?c:touchAuto(C),ko=touchFly(C,aim,{e:gauss(),d:gauss(),gust:gauss()}),z=ko.zone,sc=()=>`${displayTeam(M.f.a)} ${M.sa} – ${M.sb} ${displayTeam(M.f.b)}`,R=v=>{M.pr.v+=v},T=M.pr.tk=M.pr.tk||[0,0],ym=`${Math.max(0,Math.round(ko.y??0))} m`;
 T[1]++;if(ko.made)T[0]++;X.st.kicks++;let out;
 if(z==='try'){engSay(M,m,'kick',X,`${me.name} puts it out a metre from their line.`);R(.6);if(Math.random()<.62){scoreTry(M,X,Y,m,Math.random()<.5?'maul':'break');out={ok:true,head:'Try!',line:`A perfect kick, tapped a metre out, and they score on the next play. ${sc()}.`}}else{const r=penResolve(M,X,Y,m,'touch',{...(C.fix||{}),far:false,tk:1,tkBoost:2})||{};out={ok:r.ok===true?true:null,head:`On the line${r.head?` · ${r.head}`:''}`,line:`Out a metre from their line. ${r.line||sc()+'.'}`}}}
 else if(z==='impact'||z==='standard'||z==='short'){engSay(M,m,'kick',X,`${me.name} finds touch ${ym} from their line. Tap restart, six fresh tackles.`);R(z==='impact'?.3:z==='standard'?.08:-.05);const r=penResolve(M,X,Y,m,'touch',{...(C.fix||{}),far:z==='short',tk:1,tkBoost:z==='impact'?1.6:z==='standard'?1:.8})||{};out={ok:z==='impact'||r.ok===true?true:null,head:`${z==='impact'?'Impact':z==='standard'?'In their 20':'Far out'}${r.head?` · ${r.head}`:''}`,line:`Out ${ym} from their line. ${r.line||sc()+'.'}`}}
 else if(z==='miss'){R(-.35);engMom(M,Y,.2);engSay(M,m,'kick',X,`${me.name} misses touch! ${displayTeam(Y.team)} run it back.`);if(Math.random()<TOUCH_CTR){scoreTry(M,Y,X,m,'counter');R(-.25);out={ok:false,head:'Missed touch!',line:`It stays in play and they run it back the length of the field. ${sc()}.`}}else{Y.st.to++;out={ok:false,head:'Missed touch!',line:`It stays in play and they run it back. The chance is gone. ${sc()}.`}}}
 else{R(-.2);Y.st.to++;engMom(M,Y,.08);const why=z==='dead'?'It carries over the dead-ball line before it goes out: a 20-metre restart to them.':'It dies in their in-goal and they touch it down: a 20-metre restart to them.';engSay(M,m,'kick',X,`${me.name} kicks for touch. ${why}`);out={ok:false,head:'Kicked dead',line:`${why} ${sc()}.`}}
 return {...out,km:touchLine(C,ko),kv:kickResHTML(C,ko,C.clutch?2.3:.15),kdur:ko.dur+(C.clutch?2.3:.15)}}"""

def _extra(js, rep, resub):
    js = resub(js, r"^Object\.assign\(COLOURS,\{'Toulouse'.*$", lambda m: "", 1, 'colours-union', re.M)
    js = rep(js, "intlCareer(s)?(s.comp==='wc'?'World Cup':TIER_NAME[tierOf(s.team,s)]||'Nations Championship'):'World Cup'}", "intlCareer(s)?(s.comp==='wc'?'World Cup':'Test season'):'World Cup'}")
    js = rep(js, "intlCareer(s)&&s.comp!=='wc'?TIER_NAME[tierOf(s.team,s)]||'Nations Championship':'Rugby League World Cup'}", "intlCareer(s)&&s.comp!=='wc'?(curWin(s)?winCompName(winCompOf(s.team,curWin(s),s),curWin(s),s):'Test season'):'Rugby League World Cup'}")
    return js

_apply_main = apply
def apply(js, rep, resub, replace_function):
    return _extra(_apply_main(js, rep, resub, replace_function), rep, resub)
