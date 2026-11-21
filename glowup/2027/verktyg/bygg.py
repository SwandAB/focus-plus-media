"""Bygger månadsfiler, renderingskö och CSV från data/raw/2027-MM.json.

Kör: python3 glowup/2027/verktyg/bygg.py
Ut:  glowup/2027/manad/2027-MM.md, glowup/2027/RENDERKO.md,
     glowup/2027/data/glowup-2027.json, glowup/2027/data/glowup-2027.csv
"""
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SOUL_ID = "0b50476d-110f-4d0e-ab69-372ea8caad70"
MONTHS_SV = ["januari", "februari", "mars", "april", "maj", "juni", "juli",
             "augusti", "september", "oktober", "november", "december"]
DAYS_SV = {"Mon": "måndag", "Tue": "tisdag", "Wed": "onsdag", "Thu": "torsdag",
           "Fri": "fredag", "Sat": "lördag", "Sun": "söndag"}
ROLE_SV = {"1": "Ämneskarusell", "2": "Metodkarusell", "3": "Lågenergikarusell",
           "4": "Systemkarusell (produkt)", "5": "Söndagsgenomgång",
           "A": "Hook-reel", "B": "Metod-reel", "C": "Loop-reel"}
CTA_SLIDE = {"cta-reset": "slutsliden cta-reset (gratisguiden)",
             "cta-core": "slutsliden cta-core (FOCUS+ Core)",
             "cta-save": "slutsliden cta-save (spara inlägget)"}

# ---- Higgsfield-inställningar (från Higgsfields modellkatalog 2026-11-21) ----
IMG_FACELESS_REEL = [
    ("Verktyg", "Image"), ("Modell", "Nano Banana Pro"), ("Bildformat (aspect ratio)", "9:16"),
    ("Upplösning", "2K"), ("Referensbilder", "inga"), ("Antal", "1"),
]
IMG_AVATAR_REEL = [
    ("Verktyg", "Image"), ("Modell", "Soul 2.0 (Higgsfield Soul)"),
    ("Karaktär (Soul ID)", f"Mia v1 ({SOUL_ID})"), ("Stil", "ingen / General"),
    ("Bildformat (aspect ratio)", "9:16"), ("Kvalitet", "2K"), ("Referensbild", "ingen"), ("Antal", "1"),
]
VIDEO = [
    ("Verktyg", "Video"), ("Modell", "Seedance 2.5"),
    ("Läge", "bild till video (Omni reference), startbilden från steg 1 som Start frame"),
    ("End frame", "ingen"), ("Bildformat", "9:16"), ("Längd", "10 s"), ("Upplösning", "1080p"),
    ("Ljud (Generate audio)", "AV"), ("Bitrate", "High"), ("Draft", "AV"),
]
COVER_FACELESS = [
    ("Verktyg", "Image"), ("Modell", "Nano Banana Pro"), ("Bildformat", "4:5"),
    ("Upplösning", "2K"), ("Referensbilder", "inga"), ("Antal", "1"),
]
COVER_AVATAR = [
    ("Verktyg", "Image"), ("Modell", "Soul 2.0 (Higgsfield Soul)"),
    ("Karaktär (Soul ID)", f"Mia v1 ({SOUL_ID})"), ("Stil", "ingen / General"),
    ("Bildformat", "3:4 (Soul har inte 4:5; beskärs till 4:5 i Canva)"), ("Kvalitet", "2K"), ("Antal", "1"),
]
TEXTURE = COVER_FACELESS

TEXTURES = {
    "01": "Flat lay of unbleached ivory linen paper with a faint deckled edge, lit by low January window light from the left, very soft shadow gradient, muted nordic palette of ivory (#F5F0EA) and warm grey",
    "02": "Close view of a matte ivory plaster wall with subtle hand-troweled texture, cool late-winter daylight, muted nordic palette of ivory (#F5F0EA) and pale sage (#8A9E8C)",
    "03": "Soft sage-tinted watercolor paper texture with gentle tooth, overcast spring light, muted nordic palette of sage (#8A9E8C) and ivory (#F5F0EA)",
    "04": "Natural oat-colored linen fabric laid flat, fine weave visible, soft diffused morning light, muted nordic palette of ivory (#F5F0EA), oat and dusty rose (#C4968A)",
    "05": "Pale oak wood grain surface seen from above, fine straight grain, bright soft daylight, muted nordic palette of ivory (#F5F0EA) and light oak",
    "06": "Sheer ivory curtain fabric with diffused summer light behind it, soft folds out of focus, muted nordic palette of ivory (#F5F0EA) and warm white",
    "07": "Sun-bleached handmade cotton paper with soft long shadows of leaves falling across it, muted nordic palette of ivory (#F5F0EA) and sage (#8A9E8C)",
    "08": "Unglazed ivory ceramic surface with fine speckles, soft late-summer side light, muted nordic palette of ivory (#F5F0EA) and dusty rose (#C4968A)",
    "09": "Grey-beige wool felt texture laid flat, soft even light, muted nordic palette of warm grey, ivory (#F5F0EA) and charcoal (#2C2C2C) accents",
    "10": "Charcoal-tinted handmade paper with subtle fibers, warm lamp light from one side, muted nordic palette of warm charcoal (#2C2C2C) and ivory (#F5F0EA)",
    "11": "Dusty rose linen fabric with gentle creases, low warm afternoon light, muted nordic palette of dusty rose (#C4968A) and ivory (#F5F0EA)",
    "12": "Ivory wool knit texture in soft focus with warm candle-like light, muted nordic palette of ivory (#F5F0EA), warm charcoal (#2C2C2C) and dusty rose (#C4968A)",
}
TEX_END = ", even composition with no focal object, suitable as a quiet background for text, editorial documentary photography, soft natural grain, no text, no letters, no logos, no watermark"

TIMING = ["0,0–3,0 s", "3,0–6,5 s", "6,5–10,0 s"]


def settings_md(rows):
    return "\n".join(f"| {k} | {v} |" for k, v in [("Fält", "Val"), ("---", "---")] + rows)


def code(text):
    return "```text\n" + text.strip() + "\n```"


def strip_em(s):
    return re.sub(r"</?em>", "", s)


def reel_md(s):
    img = IMG_AVATAR_REEL if s.get("avatar") else IMG_FACELESS_REEL
    lines = "\n".join(f"{i+1}. `{t}` · \"{l}\"" for i, (t, l) in enumerate(zip(TIMING, s["hook_lines"])))
    return f"""### {s['id']} · {DAYS_SV[s['weekday']]} {s['date'][8:].lstrip('0')}/{int(s['date'][5:7])} kl {s['time_cet'].replace(':', '.')} · {ROLE_SV[s['slot']]}

Pelare {s['pillar']} · format `{s['format']}` · {'**Soul-avatar**' if s.get('avatar') else 'ansiktslös'} · CTA `{s['cta']}`

**Steg 1 · Startbild** (spara som `{s['id']}-start.png`)

{settings_md(img)}

{code(s['start_frame_prompt'])}

**Steg 2 · Video** (spara som `{s['id']}.mp4`)

{settings_md(VIDEO)}

{code(s['video_prompt'])}

**Steg 3 · Klippning och text** (Instagram-appen, CapCut eller Canva)

- Klipp till 9–10 s. Klipp bort första 0,3 s om bilden rycker i starten.{' Låt sista bildrutan gå sömlöst in i den första (loop).' if s['format'] == 'loop' else ''}
- Textrader i gemener, typsnitt Cormorant Garamond (i Instagram-appen: "Classic"), färg ivory `#F5F0EA` på mörk bild eller charcoal `#2C2C2C` på ljus bild, övre tredjedelen, ingen bakgrundsruta:
{lines}
- Musik: sök "{s['music_mood']}" i Instagrams ljudbibliotek, volym cirka 60 %. Ingen röst.
- Omslagsbild: bildrutan vid cirka 1 s med rad 1 synlig.

**Caption**

{code(s['caption'])}
"""


def carousel_md(s):
    img = COVER_AVATAR if s.get("avatar") else COVER_FACELESS
    slides = []
    for i, sl in enumerate(s["slides"], 1):
        if "shared" in sl:
            slides.append(f"{i}. {CTA_SLIDE.get(sl['shared'], sl['shared'])}")
        elif sl.get("type") == "hook":
            slides.append(f"{i}. **Omslag:** \"{strip_em(sl['text'])}\"" + (f" · underrad: \"{sl['sub']}\"" if sl.get('sub') else ""))
        else:
            p = " ".join(sl.get("p", []))
            slides.append(f"{i}. **{sl.get('num', '')} {sl['h']}** · {p}")
    slides_txt = "\n".join(slides)
    return f"""### {s['id']} · {DAYS_SV[s['weekday']]} {s['date'][8:].lstrip('0')}/{int(s['date'][5:7])} kl {s['time_cet'].replace(':', '.')} · {ROLE_SV[s['slot']]}

Pelare {s['pillar']} · {'**Soul-avatar**' if s.get('avatar') else 'ansiktslös'} · CTA `{s['cta']}`

**Omslagsbild** (spara som `{s['id']}-omslag.png`)

{settings_md(img)}

{code(s['cover_prompt'])}

**Slides** (Canva 1080×1350: rubriker Cormorant Garamond, brödtext Inter, siffror JetBrains Mono; inre slides på månadens textur eller ren ivory/sage/rose)

{slides_txt}

**Caption**

{code(s['caption'])}
"""


def main():
    allrows = []
    for f in sorted(RAW.glob("2027-*.json")):
        allrows += json.loads(f.read_text())
    allrows.sort(key=lambda s: (s["date"], s["time_cet"]))
    (ROOT / "data" / "glowup-2027.json").write_text(json.dumps(allrows, indent=1, ensure_ascii=False))

    with open(ROOT / "data" / "glowup-2027.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "datum", "tid", "typ", "roll", "veckotema", "pelare", "avatar", "steg", "modell",
                    "bildformat", "langd", "upplosning", "prompt", "textrader", "caption", "klar"])
        for s in allrows:
            if s["kind"] == "reel":
                m1 = "Soul 2.0 (Mia v1)" if s.get("avatar") else "Nano Banana Pro"
                w.writerow([s["id"], s["date"], s["time_cet"], "reel", ROLE_SV[s["slot"]], s["week_theme"], s["pillar"],
                            s.get("avatar", False), "1 startbild", m1, "9:16", "", "2K", s["start_frame_prompt"],
                            " / ".join(s["hook_lines"]), s["caption"], ""])
                w.writerow([s["id"], s["date"], s["time_cet"], "reel", ROLE_SV[s["slot"]], s["week_theme"], s["pillar"],
                            s.get("avatar", False), "2 video", "Seedance 2.5 (start frame, ljud av)", "9:16", "10 s",
                            "1080p", s["video_prompt"], "", "", ""])
            else:
                m1 = "Soul 2.0 (Mia v1)" if s.get("avatar") else "Nano Banana Pro"
                w.writerow([s["id"], s["date"], s["time_cet"], "karusell", ROLE_SV[s["slot"]], s["week_theme"], s["pillar"],
                            s.get("avatar", False), "omslag", m1, "3:4" if s.get("avatar") else "4:5", "", "2K",
                            s["cover_prompt"], strip_em(s["slides"][0].get("text", "")), s["caption"], ""])

    (ROOT / "manad").mkdir(exist_ok=True)
    stats = []
    for mi in range(1, 13):
        mm = f"{mi:02d}"
        rows = [s for s in allrows if s["date"][5:7] == mm]
        if not rows:
            continue
        reels = [s for s in rows if s["kind"] == "reel"]
        cars = [s for s in rows if s["kind"] == "carousel"]
        av = sum(1 for s in rows if s.get("avatar"))
        weeks = []
        for s in rows:
            label = f"V{s['iso_week']:02d}" if s["iso_week"] else "V53/2026"
            if (label, s["week_theme"]) not in weeks:
                weeks.append((label, s["week_theme"]))
        wk = "\n".join(f"- {a}: {b}" for a, b in weeks)
        head = f"""# {MONTHS_SV[mi-1].capitalize()} 2027 · {rows[0]['month_theme']}

Prompter för glowup.architect. {len(reels)} Reels och {len(cars)} karuseller, varav {av} med Soul-avataren.
Strategi och regler: [STRATEGI-2027.md](../STRATEGI-2027.md). Renderingsordning: [RENDERKO.md](../RENDERKO.md).

**Före första prompten:** kontrollera att Unlimited är påslaget i Higgsfield (modeller med
Unlim-märke: Seedance 2.5, Nano Banana Pro och Soul 2.0), så att inget drar credits. Om
1080p inte ingår i Unlimited: välj högsta upplösning som har Unlim-märket.

Veckoteman:
{wk}

## Innehåll
1. [Reels](#reels) (steg 1 startbild, steg 2 video, steg 3 klippning)
2. [Karuseller](#karuseller) (omslagsbild + slidetexter)
3. [Månadens textur](#manadens-textur) (bakgrund för inre slides)

## Reels

"""
        body = "\n---\n\n".join(reel_md(s) for s in reels)
        body += "\n\n## Karuseller\n\n" + "\n---\n\n".join(carousel_md(s) for s in cars)
        tex = TEXTURES[mm] + TEX_END
        body += f"""

## Månadens textur

En bild som bakgrund till alla inre slides den här månaden (spara som `2027-{mm}-textur.png`).
Lägg den med 85–90 % ivory-överlägg i Canva så att texten blir lättläst.

{settings_md(TEXTURE)}

{code(tex)}
"""
        (ROOT / "manad" / f"2027-{mm}.md").write_text(head + body)
        stats.append((mm, len(reels), len(cars), av))

    tr = sum(r for _, r, _, _ in stats)
    tc = sum(c for _, _, c, _ in stats)
    gens = tr * 2 + tc + len(stats)
    table = "\n".join(f"| [{MONTHS_SV[int(m)-1]}](manad/2027-{m}.md) | {r} | {r} | {c} | 1 | {a} |" for m, r, c, a in stats)
    (ROOT / "RENDERKO.md").write_text(f"""# Renderingskö för 24-timmarspasset i Higgsfield

Totalt **{gens} genereringar**: {tr} startbilder + {tr} videor + {tc} karusellomslag + {len(stats)} texturer.
På 24 timmar är det i snitt en generering var {round(24*60/gens, 1)} minut. Higgsfield kör flera
genereringar samtidigt, så starta nästa medan föregående renderar.

## Ordning

1. **Pass 1 · Reels januari–mars** (Q1 testar formaten och är viktigast). För varje Reel: steg 1
   startbild, välj den bästa, sedan steg 2 video med den som Start frame.
2. **Pass 2 · Reels april–december.**
3. **Pass 3 · Karusellomslag**, månad för månad.
4. **Pass 4 · Månadens textur** (12 st).

Om tiden tar slut: karusellerna fungerar som ren text på ivory, sage eller rose, precis som i
november–december 2026. Reels kan inte ersättas, så prioritera pass 1 och 2.

## Arbetssätt som sparar tid

- Ha månadsfilen öppen bredvid Higgsfield. Varje prompt ligger i en kodruta med kopieringsknapp.
- Gör alla startbilder för en vecka först, sedan alla videor för samma vecka. Då byter du modell
  mer sällan.
- Spara med filnamnet som står vid varje steg, till exempel `2027-01-04-R-A.mp4`. Lägg allt i en
  mapp per månad. Då kan Claude ladda upp och schemalägga i Postiz efteråt.
- Blir en video fel (konstig hand, flimmer, text i bild): kör om samma prompt en gång. Blir den
  fel igen, hoppa över och markera id:t, så skriver Claude om prompten.
- Bocka av i `data/glowup-2027.csv` (kolumnen `klar`) eller bara i mappen.

## Per månad

| Månad | Startbilder | Videor | Karusellomslag | Textur | Varav Soul-avatar |
|---|---|---|---|---|---|
{table}

## Fält som gäller alla prompter

| Steg | Modell | Fält och val |
|---|---|---|
| Reel steg 1, ansiktslös | Nano Banana Pro | Image · 9:16 · 2K · inga referensbilder · antal 1 |
| Reel steg 1, avatar | Soul 2.0 | Image · Karaktär Mia v1 · stil General · 9:16 · 2K · antal 1 |
| Reel steg 2 | Seedance 2.5 | Video · bild till video (Start frame = startbilden) · 9:16 · 10 s · 1080p · ljud AV · bitrate High · Draft AV |
| Karusellomslag, ansiktslös | Nano Banana Pro | Image · 4:5 · 2K · antal 1 |
| Karusellomslag, avatar | Soul 2.0 | Image · Karaktär Mia v1 · 3:4 (beskärs till 4:5) · 2K |
| Textur | Nano Banana Pro | Image · 4:5 · 2K |

**Reserv om Seedance 2.5 krånglar:** Seedance 2.0 (också Unlim) med samma val plus Mode `std`
och Genre `auto`. Kling 3.0 fungerar också (Start frame, 9:16, 10 s, Mode `pro`, Sound `off`) men
har inte Unlim-märket och drar credits.

**Varför ljudet är av:** Seedance kan skapa eget ljud, ibland röster. Reglerna säger ingen
syntetisk röst, så musiken läggs på i Instagram i stället.

**Varför ingen text i bilden:** videomodeller stavar ofta fel. Därför slutar varje prompt med
"no text, no letters" och raderna läggs på i steg 3.
""")
    print("klart", stats, "genereringar", gens)


if __name__ == "__main__":
    main()
