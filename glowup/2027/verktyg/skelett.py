"""Bygger tomma platser (slots) för 2027 per månad: glowup/2027/data/skelett/2027-MM.json.

Kör: python3 glowup/2027/verktyg/skelett.py
"""
import datetime as dt, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRAT = (ROOT / "STRATEGI-2027.md").read_text()

# veckoteman ur strategin: "- V05: the 2-out-of-5 day" och "- V53/2026 (1–3/1): ..."
themes = {}
month_theme = {}
cur = None
for line in STRAT.splitlines():
    m = re.match(r"### (\w+) · (.+)", line)
    if m:
        cur = m.group(2).split(" (")[0]
        continue
    m = re.match(r"- V(\d+)(/2026)?[^:]*: (.+)", line)
    if m and cur:
        key = 0 if m.group(2) else int(m.group(1))
        themes[key] = (m.group(3).replace(" (inget 24–25/12)", ""), cur)

PRESCHEDULED_MONDAYS = {dt.date(2027,1,4)+dt.timedelta(weeks=i) for i in range(9)}  # 4/1–1/3
SKIP = {dt.date(2027,12,24), dt.date(2027,12,25)}

# weekday -> list of (kind, slot, time, role)
PLAN = {
    0: [("C","1","12:30","topic: veckans ämne, sparbar"), ("R","A","19:00","hook-reel byggd för sends")],
    1: [("C","2","12:30","method: metod steg för steg")],
    2: [("R","B","19:00","metod-reel: ett konkret verktyg")],
    3: [("C","3","09:00","low-energy: lågenergi-varianten av veckans ämne")],
    4: [("C","4","12:30","system: hur FOCUS+ Core gör det (produkt)")],
    5: [("R","C","10:00","loop-reel: lugn, loopbar, sparvänlig")],
    6: [("C","5","19:00","sunday review: söndagsgenomgång inför veckan")],
}
out = {}
d = dt.date(2027,1,1)
while d.year == 2027:
    iso = d.isocalendar()
    wk = 0 if iso[0] == 2026 else iso[1]
    theme, mtheme = themes[wk]
    for kind, slot, time, role in PLAN[d.weekday()]:
        if d in SKIP: continue
        if kind == "C" and slot == "1" and d in PRESCHEDULED_MONDAYS: continue
        out.setdefault(d.strftime("%Y-%m"), []).append({
            "id": f"{d.isoformat()}-{kind}-{slot}",
            "date": d.isoformat(), "weekday": d.strftime("%a"), "time_cet": time,
            "kind": "reel" if kind == "R" else "carousel", "slot": slot, "role": role,
            "iso_week": wk, "week_theme": theme, "month_theme": mtheme,
        })
    d += dt.timedelta(1)
(ROOT / "data/skelett").mkdir(parents=True, exist_ok=True)
tot = {"reel":0,"carousel":0}
for k, v in out.items():
    (ROOT / f"data/skelett/{k}.json").write_text(json.dumps(v, indent=1, ensure_ascii=False))
    for s in v: tot[s["kind"]] += 1
    print(k, len(v), sum(s["kind"]=="reel" for s in v))
print(tot)
