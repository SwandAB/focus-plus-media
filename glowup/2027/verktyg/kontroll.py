"""Regelkontroll av data/raw/2027-*.json mot skelettet och varumärkesreglerna.

Kör: python3 glowup/2027/verktyg/kontroll.py   (exit 1 vid fel)
"""
import json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANNED_WORDS = ["discovery", "transformation", "journey", "game-changing", "game changing", "girlboss",
                "manifest", "hormone-friendly", "hormone-aware", "magic", "amazing", "perfect for",
                "obsessed", "breakthrough", "toolkit", "science-backed", "hack", "@focusplus",
                "@glowup_architect", "sale", "discount", "% off"]
BANNED_PROMPT = ["bare skin", "kodak", "portra", "film border", "close-up portrait", "looking at camera",
                 "looking toward camera", "eye contact", "smiling at viewer", "talking", "speaking",
                 " lip", "mouth", "child", "kid", "baby", "apple logo"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
errors, warns = [], []
hooks = Counter()

for sk in sorted((ROOT / "data/skelett").glob("2027-*.json")):
    raw = ROOT / "data/raw" / sk.name
    if not raw.exists():
        errors.append(f"{sk.name}: saknas i raw")
        continue
    S, R = json.loads(sk.read_text()), json.loads(raw.read_text())
    if [s["id"] for s in S] != [r.get("id") for r in R]:
        errors.append(f"{sk.name}: id-listan matchar inte skelettet ({len(S)} vs {len(R)})")
    weekav = Counter()
    for r in R:
        i = r.get("id")
        text = json.dumps({k: r.get(k) for k in ("caption", "hook_lines", "slides")}, ensure_ascii=False).lower()
        for w in BANNED_WORDS:
            if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", text):
                errors.append(f"{i}: förbjudet ord '{w}'")
        cap = r.get("caption", "")
        if len(EMOJI.findall(cap.replace("🤍", ""))) or cap.count("🤍") > 1:
            errors.append(f"{i}: emoji i caption")
        n = len(cap.split())
        if not 30 <= n <= 140:
            warns.append(f"{i}: caption {n} ord")
        if r.get("pillar") == "P5" and "FOCUS+ Core is our own product." not in cap:
            warns.append(f"{i}: P5 utan 'FOCUS+ Core is our own product.'")
        prompts = [r.get("start_frame_prompt"), r.get("cover_prompt")]
        for p in filter(None, prompts):
            pl = p.lower()
            for w in BANNED_PROMPT:
                if w in pl:
                    errors.append(f"{i}: förbjuden promptfras '{w.strip()}'")
            if "no logos" not in pl or "no text" not in pl:
                errors.append(f"{i}: bildprompt saknar 'no text'/'no logos'")
            if r.get("avatar") and not p.startswith("A woman"):
                errors.append(f"{i}: avatarprompt börjar inte med 'A woman'")
        if r["kind"] == "reel":
            hl = r.get("hook_lines") or []
            if len(hl) != 3:
                errors.append(f"{i}: {len(hl)} hookrader")
            for h in hl:
                if EMOJI.search(h):
                    errors.append(f"{i}: emoji i hook")
            hooks[hl[0].strip().lower() if hl else ""] += 1
            vp = (r.get("video_prompt") or "").lower()
            if "no lip movement" not in vp or "no text" not in vp:
                errors.append(f"{i}: videoprompt saknar 'no text'/'no lip movement'")
            vp_body = vp.replace("no people speaking", "").replace("no lip movement", "")
            for w in BANNED_PROMPT:
                if w in vp_body:
                    errors.append(f"{i}: förbjuden fras i videoprompt '{w.strip()}'")
            for k in ("format", "music_mood", "pillar", "cta", "start_frame_prompt"):
                if not r.get(k):
                    errors.append(f"{i}: saknar {k}")
            if r.get("avatar"):
                weekav[("R", r["iso_week"])] += 1
        else:
            sl = r.get("slides") or []
            if not sl or sl[0].get("type") != "hook" or "shared" not in sl[-1]:
                errors.append(f"{i}: slides saknar hook först eller delad slutslide sist")
            body = [x for x in sl if x.get("type") == "body"]
            if not 3 <= len(body) <= 5:
                errors.append(f"{i}: {len(body)} body-slides")
            hooks[re.sub(r"</?em>", "", sl[0].get("text", "")).strip().lower() if sl else ""] += 1
            if r.get("avatar"):
                weekav[("C", r["iso_week"])] += 1
    for (k, wk), n in weekav.items():
        if (k == "R" and n > 1) or (k == "C" and n > 1):
            errors.append(f"{sk.name} V{wk}: {n} avatar-{k} samma vecka")

for h, n in hooks.items():
    if n > 1 and h:
        errors.append(f"upprepad hook ({n}x): {h}")

print(f"{len(errors)} fel, {len(warns)} varningar")
for e in errors:
    print("FEL ", e)
for w in warns[:60]:
    print("VARN", w)
sys.exit(1 if errors else 0)
