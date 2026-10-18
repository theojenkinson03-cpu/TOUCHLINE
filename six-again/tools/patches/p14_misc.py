"""World Club Series sizes and World Cup descriptions."""
import re

def apply(js, rep, resub, replace_function):
    js = rep(js, "The top 24 at the end of the season qualify for th", "The top 16 at the end of the season qualify for th")
    js = rep(js, "The line under 24th marks", "The line under 16th marks")
    js = rep(js, "'Clear of 25th':'Behind 24th'", "'Clear of 17th':'Behind 16th'")
    js = rep(js, "'Top 24 play the World Club Series'", "'Top 16 play the World Club Series'")
    js = rep(js, "Every club in all four leagues on one ladder.", "Every NRL and Super League club on one ladder.")
    js = rep(js, "Results from all four leagues count,", "Results from both leagues count,")
    js = resub(js, r"cwc\?'Six pools of four, drawn from the top 24 clubs in the World Ranking\. Top two plus four best third-placed teams advance to a seeded knockout\.':\(intlCareer\(s\)&&s\.year!==2027\?`.*?`:'.*?'\)",
               lambda m: "cwc?'Four pools of four, drawn from the top 16 clubs in the World Ranking. The top two in each pool reach the quarter-finals.':'Group A plays a round robin; Groups B and C play each other on one combined table. The top two of each reach the semi-finals.'", 1, 'cwcdesc', re.S)
    return js
