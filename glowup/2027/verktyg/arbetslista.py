"""Bygger en enda arbetslista för 24-timmarspasset i Higgsfield, i RENDERKO-ordning.

Kör: python3 glowup/2027/verktyg/arbetslista.py
Ut:  glowup/2027/ARBETSLISTA.md och glowup/2027/arbetslista.html (kopieringsknappar + bockar)
"""
import html, json
from pathlib import Path

import bygg  # samma mapp

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "data" / "glowup-2027.json").read_text())
reels = [s for s in rows if s["kind"] == "reel"]
cars = [s for s in rows if s["kind"] == "carousel"]
MAPP = "Skrivbordet → mappen glowup-2027 → undermapp per månad (01, 02 …)"


def img_settings(s, cover):
    if s.get("avatar"):
        return ("Image · Soul 2.0 · Karaktär: Mia v1 · Stil: General · "
                + ("3:4 (beskärs till 4:5 i Canva)" if cover else "9:16") + " · 2K · antal 1")
    return "Image · Nano Banana Pro · " + ("4:5" if cover else "9:16") + " · 2K · inga referensbilder · antal 1"


items = []
def add(pas, s, steg, fil, inst, prompt, extra=""):
    items.append(dict(pas=pas, id=s["id"] if s else fil, steg=steg, fil=fil, inst=inst, prompt=prompt.strip(),
                      extra=extra, man=(s["date"][5:7] if s else fil[5:7])))

for pas, sel in ((1, [r for r in reels if r["date"] < "2027-04"]), (2, [r for r in reels if r["date"] >= "2027-04"])):
    for s in sel:
        add(pas, s, "Startbild", f"{s['id']}-start.png", img_settings(s, False), s["start_frame_prompt"])
        add(pas, s, "Video", f"{s['id']}.mp4",
            f"Video · Seedance 2.5 · Start frame: {s['id']}-start.png · End frame: ingen · 9:16 · 10 s · 1080p · "
            "Generate audio AV · Bitrate High · Draft AV", s["video_prompt"],
            "Textrader läggs på senare (står i månadsfilen), inget att göra nu.")
for s in cars:
    add(3, s, "Karusellomslag", f"{s['id']}-omslag.png", img_settings(s, True), s["cover_prompt"])
for mm, t in bygg.TEXTURES.items():
    add(4, None, "Månadens textur", f"2027-{mm}-textur.png",
        "Image · Nano Banana Pro · 4:5 · 2K · antal 1", t + bygg.TEX_END)

PASS = {1: "Pass 1 · Reels januari–mars", 2: "Pass 2 · Reels april–december",
        3: "Pass 3 · Karusellomslag", 4: "Pass 4 · Månadens textur"}
N = len(items)

# ---------- Markdown ----------
md = [f"""# Arbetslista Higgsfield 2027 · {N} genereringar

Gå uppifrån och ner. Varje rad: välj inställningarna, klistra in prompten, generera, ladda ner
och spara med exakt filnamn i {MAPP}.
Kontrollera först att Unlimited är påslaget. Om 1080p eller 2K inte har Unlimited-märket: välj
högsta upplösning som har det.

Interaktiv version med kopieringsknappar och bockar: `arbetslista.html` (öppna i webbläsaren).
"""]
cur = None
for i, it in enumerate(items, 1):
    if it["pas"] != cur:
        cur = it["pas"]
        md.append(f"\n## {PASS[cur]}\n")
    md.append(f"### {i}/{N} · {it['steg']} · spara som `{it['fil']}`\n\n**Val:** {it['inst']}\n\n```text\n{it['prompt']}\n```\n")
(ROOT / "ARBETSLISTA.md").write_text("\n".join(md))

# ---------- HTML ----------
blocks, cur = [], None
for i, it in enumerate(items, 1):
    if it["pas"] != cur:
        cur = it["pas"]
        blocks.append(f'<h2 id="p{cur}">{PASS[cur]}</h2>')
    e = html.escape
    blocks.append(f'''<section class="item" data-k="{e(it['fil'])}">
<div class="top"><label><input type="checkbox"> <b>{i}/{N}</b> · {e(it['steg'])}</label>
<span class="fn">spara som <code>{e(it['fil'])}</code> <button class="cp" data-t="{e(it['fil'])}">kopiera namn</button></span></div>
<div class="inst">{e(it['inst'])}</div>
<pre>{e(it['prompt'])}</pre><button class="cp big">kopiera prompt</button>
{f'<div class="ex">{e(it["extra"])}</div>' if it['extra'] else ''}
</section>''')

page = f'''<!doctype html><html lang="sv"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Higgsfield 2027</title>
<style>
:root{{--bg:#F5F0EA;--ink:#2C2C2C;--sage:#8A9E8C;--rose:#C4968A;--card:#fff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1f1f1f;--ink:#eee;--card:#2a2a2a}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,sans-serif}}
header{{position:sticky;top:0;background:var(--bg);padding:12px 16px;border-bottom:1px solid var(--sage);z-index:2}}
header a{{color:var(--ink);margin-right:12px}} main{{max-width:900px;margin:auto;padding:0 16px 80px}}
h2{{font-family:Georgia,serif;margin-top:32px}} .item{{background:var(--card);border-radius:10px;padding:12px 14px;margin:12px 0;border-left:4px solid var(--sage)}}
.item.done{{opacity:.45;border-left-color:var(--rose)}} .top{{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}}
.inst{{margin:6px 0;font-weight:600}} pre{{white-space:pre-wrap;background:rgba(138,158,140,.15);padding:10px;border-radius:6px;font:13px/1.45 ui-monospace,monospace}}
button{{border:1px solid var(--sage);background:transparent;color:var(--ink);border-radius:6px;padding:4px 10px;cursor:pointer}}
button.big{{padding:8px 16px;font-weight:600}} button.ok{{background:var(--sage);color:#fff}} .ex{{font-size:13px;opacity:.8;margin-top:6px}}
input[type=checkbox]{{transform:scale(1.4);margin-right:6px}} #hide{{margin-left:8px}}
</style></head><body>
<header><b>Higgsfield 2027</b> · <span id="cnt"></span> klara av {N}
<label id="hide"><input type="checkbox" id="hd"> dölj klara</label><br>
<a href="#p1">Pass 1</a><a href="#p2">Pass 2</a><a href="#p3">Pass 3</a><a href="#p4">Pass 4</a>
<a href="#" id="next">hoppa till nästa</a></header>
<main><p>Spara varje fil med exakt namn i {html.escape(MAPP)}. Kontrollera att Unlimited är påslaget.
Bockarna sparas i den här webbläsaren.</p>
{"".join(blocks)}</main>
<script>
const K="hf2027";let st={{}};try{{st=JSON.parse(localStorage.getItem(K)||"{{}}")}}catch(e){{}}
const save=()=>{{try{{localStorage.setItem(K,JSON.stringify(st))}}catch(e){{}}}};
const items=[...document.querySelectorAll(".item")];
function upd(){{let n=0;items.forEach(s=>{{const d=!!st[s.dataset.k];s.classList.toggle("done",d);s.querySelector("input").checked=d;if(d)n++;
s.style.display=(d&&document.getElementById("hd").checked)?"none":""}});document.getElementById("cnt").textContent=n}}
items.forEach(s=>s.querySelector("input").addEventListener("change",e=>{{st[s.dataset.k]=e.target.checked;save();upd()}}));
document.getElementById("hd").addEventListener("change",upd);
document.querySelectorAll("button.cp").forEach(b=>b.addEventListener("click",()=>{{
 const t=b.dataset.t||b.previousElementSibling.textContent;navigator.clipboard.writeText(t).then(()=>{{const o=b.textContent;b.textContent="kopierat";b.classList.add("ok");setTimeout(()=>{{b.textContent=o;b.classList.remove("ok")}},1200)}})}}));
document.getElementById("next").addEventListener("click",e=>{{e.preventDefault();const n=items.find(s=>!st[s.dataset.k]);if(n)n.scrollIntoView({{behavior:"smooth"}})}});
upd();
</script></body></html>'''
(ROOT / "arbetslista.html").write_text(page)
print(N, "poster")
