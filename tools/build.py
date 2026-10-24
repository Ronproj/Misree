"""Misree Chai static site generator (simple modern edition).
Usage: python3 tools/build.py OUTDIR [--artifact]
Pages reference photos at assets/img/<name>.jpg, with 520px copies in assets/img/sm/ for cards and lists."""
import os, sys, html, json
from urllib.parse import quote_plus

OUT = sys.argv[1]
ARTIFACT = "--artifact" in sys.argv

LOCATIONS = [
    dict(id="jersey-city", name="Jersey City", line1="789 Newark Ave", line2="Jersey City, NJ 07306",
         query="Misree Chai, 789 Newark Ave, Jersey City, NJ 07306", phone="(856) 210-2029", tax=0.06625, lat=40.7353, lng=-74.0617),
    dict(id="jackson-heights", name="Jackson Heights", line1="72-35 Broadway", line2="Jackson Heights, NY 11372",
         query="Misree Chai NY, 72-35 Broadway, Jackson Heights, NY 11372", phone="", tax=0.08875, lat=40.7467, lng=-73.8935),
]
for L in LOCATIONS:
    L["embed"] = f"https://www.google.com/maps?q={quote_plus(L['query'])}&z=16&output=embed"
    L["dir"] = f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(L['query'])}"
DOORDASH = "https://www.doordash.com/store/misree-chai-jersey-city-33169529/"
UBER = "https://www.ubereats.com/store/misree-chai/WD4OQXx5XaaWosChalkFYA"
INSTA = "https://www.instagram.com/misreechai/"
# Set these to the Misree Chai app's store links once known.
APP_STORE = None
PLAY_STORE = None

def store_btn(url, small, big):
    if url:
        return f'<a class="store" href="{url}" target="_blank" rel="noopener"><small>{small}</small><b>{big}</b></a>'
    return f'<span class="store" aria-disabled="true" title="Link coming soon"><small>{small}</small><b>{big}</b></span>'

# Menu data from the cafe's DoorDash / Uber Eats listings and misreechai.com search snippets.
# opts names an entry in OPTIONS (the demo ordering choices for that category).
CATS = [
    dict(slug="chai", name="Chai & Coffee", opts="hot",
         items=[("Masala Chai", "4.00", "masala-chai", "Slow-brewed with whole spices."), ("Zafrani Chai", "3.49", "zafrani-chai", "Saffron chai, sweetened the old way."),
                ("South Indian Coffee", "4.00", "south-indian-coffee", "Strong filter coffee with frothed milk.")]),
    dict(slug="kulfi", name="Kulfi Milk Tea", opts="iced",
         items=[("Falooda Kulfi", "7.49", "falooda-kulfi", "Falooda-inspired creamy milk tea."),
                ("Mango Kulfi", "7.49", "mango-kulfi", ""), ("Pista Kulfi", "7.49", "pista-kulfi", "")]),
    dict(slug="teas", name="Milk & Fruit Teas", opts="iced",
         items=[("Classic Milk Tea", "6.49", "classic-milk-tea", ""), ("Taro Milk Tea", "6.49", "taro-milk-tea", ""),
                ("Strawberry Milk Tea", "6.49", "strawberry-milk-tea", ""), ("Mango Fruit Tea", "5.49", "mango-fruit-tea", ""),
                ("Strawberry Fruit Tea", "5.49", "strawberry-fruit-tea", ""), ("Peach Fruit Tea", "5.49", "peach-fruit-tea", ""),
                ("Lychee Refresher", "5.99", "lychee-refresher", "")]),
    dict(slug="crepes", name="Crepes", opts="food",
         items=[("Triple Chocolate Crepe", "14.00", "triple-chocolate-crepe", "Kinder Bueno, Ferrero, Nutella and chocolate chips."),
                ("Nutella Crepe", "13.99", "nutella-crepe", ""), ("Royal Pistachio Crepe", "13.99", "royal-pistachio-crepe", ""),
                ("Fudge Brownie Crepe", "12.99", "fudge-brownie-crepe", ""), ("Oreo Crepe", "13.99", "oreo-crepe", ""),
                ("Mix Berries Crepe", "13.99", "mix-berries-crepe", "")]),
    dict(slug="bowls", name="Bowls", opts="food",
         items=[("Nutella Acai Bowl", "12.99", "nutella-acai-bowl", ""), ("Almond Lover Bowl", "13.99", "almond-lover-bowl", ""),
                ("Coconut Honey Bowl", "13.99", "coconut-honey-bowl", ""), ("Protein Bowl", "12.99", "protein-bowl", "")]),
    dict(slug="bakery", name="Bakery", opts="food",
         items=[("Bun Maska", "4.49", "bun-maska", "Soft bun with a thick layer of butter."), ("Butter Croissant", "4.00", "butter-croissant", ""),
                ("Nutella Croissant", "5.00", "nutella-croissant", "")]),
]
OPTIONS = {
    "hot": [("Sweetness", ["Regular", "Less sweet", "No sugar"])],
    "iced": [("Sweetness", ["Regular", "Less sweet", "No sugar"]), ("Ice", ["Regular ice", "Light ice", "No ice"])],
    "food": [],
}
GROUPS = [("drinks", "Drinks", ["chai", "kulfi", "teas"]), ("crepes", "Crepes", ["crepes"]),
          ("bowls", "Bowls", ["bowls"]), ("bakery", "Bakery", ["bakery"])]
BYSLUG = {c["slug"]: c for c in CATS}

def img(name): return f"assets/img/{name}.jpg"
def sm(name): return f"assets/img/sm/{name}.jpg"
def slug(s): return s.lower().replace(" ", "-").replace("&", "and")
def esc(s): return html.escape(s, quote=True)

CSS = r"""
/* Simple modern cafe: warm white, olive from the logo, near-black ink. Mobile first. */
:root{
  --bg:#f5ecdc; --surface:#fffaf2; --soft:#efe4d0; --ink:#2b1d14; --muted:#6e6253; --line:#e6d9c3;
  --olive:#5f5820; --olive-soft:#ece5cc; --on-ink:#ffffff; --rose:#9a4434; --gold:#c9a55a; --night:#2b1d14;
  --hh:60px; --tab:64px; --safe-b:env(safe-area-inset-bottom,0px);
  --font:"Jost","Futura","Century Gothic",system-ui,-apple-system,"Segoe UI",sans-serif;
  --r:18px; --shadow:0 1px 2px rgba(29,27,22,.05),0 8px 24px rgba(29,27,22,.07);
  color-scheme:light;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%;scroll-padding-top:calc(var(--hh) + 64px)}
body{margin:0;background:var(--bg) url(assets/img/wallpaper.svg) repeat;background-size:120px 170px;color:var(--ink);font:400 16px/1.55 var(--font);-webkit-font-smoothing:antialiased;
  padding-bottom:calc(var(--tab) + var(--safe-b));-webkit-tap-highlight-color:transparent}
a{color:inherit}
img{max-width:100%;height:auto;display:block}
button{font:inherit;color:inherit}
.wrap{max-width:1180px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1,h2,h3{font-weight:400;line-height:1.08;letter-spacing:-.015em;margin:0;text-wrap:balance}
h1{font-size:clamp(2.4rem,9vw,4.6rem);font-weight:300}
h2{font-size:clamp(1.8rem,6vw,2.8rem);font-weight:300}
p{margin:0}
.eyebrow{font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;font-weight:600;color:var(--olive);margin-bottom:10px}
.muted{color:var(--muted)}
:focus-visible{outline:2.5px solid var(--olive);outline-offset:2px;border-radius:8px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 22px;border-radius:999px;border:0;
  background:var(--ink);color:var(--on-ink);text-decoration:none;font-weight:500;font-size:1rem;cursor:pointer;transition:transform .15s,opacity .15s}
.btn:active{transform:scale(.97)}
.btn.line{background:transparent;color:var(--ink);box-shadow:inset 0 0 0 1.5px var(--ink)}
.btn.olive{background:var(--olive)}
.btn.block{width:100%}
.btn[disabled]{opacity:.4;cursor:not-allowed}
section.pad{padding-block:48px}
@media (min-width:760px){section.pad{padding-block:80px}}
.head{display:flex;justify-content:space-between;align-items:end;gap:16px;margin-bottom:20px}
.head a{font-weight:500;color:var(--olive);text-decoration:none;white-space:nowrap;padding:10px 0}

/* header */
.top{position:sticky;top:0;z-index:30;background:rgba(255,250,242,.95);backdrop-filter:saturate(1.4) blur(12px);-webkit-backdrop-filter:saturate(1.4) blur(12px);border-bottom:1px solid var(--line);padding-top:env(safe-area-inset-top,0px)}
.top .wrap{display:flex;align-items:center;gap:20px;height:var(--hh)}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;font-size:1.3rem;letter-spacing:.01em}
.brand img{width:36px;height:36px;border-radius:50%;border:1px solid var(--line)}
.brand small{font-size:.6rem;letter-spacing:.28em;text-transform:uppercase;color:var(--muted)}
.nav{display:none;gap:4px;margin-left:auto}
.nav a{text-decoration:none;padding:8px 14px;border-radius:999px;color:var(--muted);font-weight:500;font-size:.95rem}
.nav a:hover{color:var(--ink)}
.nav a[aria-current]{color:var(--ink);background:var(--soft)}
.top .btn{min-height:40px;padding:0 18px;font-size:.92rem;margin-left:auto}
@media (min-width:900px){:root{--hh:72px;--tab:0px}.nav{display:flex}.top .btn{margin-left:8px}}

/* bottom tab bar (phones and tablets) */
.tabbar{position:fixed;left:0;right:0;bottom:0;z-index:40;display:grid;grid-template-columns:repeat(5,1fr);background:rgba(255,255,255,.96);
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-top:1px solid var(--line);padding:0 env(safe-area-inset-right,0px) var(--safe-b) env(safe-area-inset-left,0px)}
.tabbar a{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;height:var(--tab);text-decoration:none;color:var(--muted);font-size:.7rem;font-weight:500}
.tabbar svg{width:23px;height:23px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.tabbar a[aria-current]{color:var(--olive)}
.tabbar a.order span{background:var(--ink);color:#fff;width:46px;height:30px;border-radius:999px;display:grid;place-items:center}
.tabbar a.order svg{width:19px;height:19px}
@media (min-width:900px){.tabbar{display:none}}

/* home */
.hero{padding-block:24px 40px}
.hero .wrap{display:grid;gap:24px}
.hero .lede{font-size:1.1rem;color:var(--muted);max-width:38ch;margin:14px 0 22px}
.hero .ctas{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.hero figure{margin:0;position:relative}
.hero figure img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:22px}
.hero .chip{position:absolute;left:12px;bottom:12px;background:rgba(255,255,255,.94);border-radius:14px;padding:10px 14px;font-size:.85rem;box-shadow:var(--shadow)}
.hero .chip b{display:block;font-weight:600}
@media (min-width:860px){.hero{padding-block:56px 72px}.hero .wrap{grid-template-columns:1fr 1.05fr;gap:56px;align-items:center}.hero .ctas{display:flex}.hero figure img{aspect-ratio:5/4}}

.cats{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-padding-inline:16px;margin:0 -16px;padding:2px 16px 8px;scrollbar-width:none}
.cats::-webkit-scrollbar{display:none}
.cat{flex:0 0 136px;scroll-snap-align:start;text-decoration:none}
.cat img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:999px 999px 16px 16px;margin-bottom:10px;outline:1.5px solid var(--gold);outline-offset:4px}
.cat{text-align:center;padding-top:6px}
.cat b{font-weight:500;display:block;line-height:1.25}
.cat span{font-size:.85rem;color:var(--muted)}
@media (min-width:900px){.cats{display:grid;grid-template-columns:repeat(6,1fr);overflow:visible;margin:0;padding:0}.cat{flex:none}}

.picks{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.pick{background:var(--surface);border-radius:999px 999px 18px 18px;border:1.5px solid var(--gold);padding:6px 6px 0;overflow:hidden;text-decoration:none;box-shadow:var(--shadow);display:flex;flex-direction:column}
.pick img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:999px 999px 12px 12px}
.pick div{text-align:center}
.pick div{padding:12px 14px 14px}
.pick b{font-weight:500;display:block;line-height:1.25}
.pick span{color:var(--muted);font-size:.9rem}
@media (min-width:900px){.picks{grid-template-columns:repeat(4,1fr);gap:20px}}

.promo{display:grid;gap:20px;background:var(--night) url(assets/img/wallpaper-dark.svg);background-size:120px 170px;border:1.5px solid rgba(201,165,90,.5);color:#fff;border-radius:26px;padding:28px 22px;overflow:hidden}
.promo .eyebrow{color:#d8cf98}
.promo p.muted{color:rgba(255,255,255,.72);margin:10px 0 20px}
.promo .btn{background:#fff;color:var(--ink)}
.promo img{border-radius:999px 999px 18px 18px;width:100%;max-width:340px;justify-self:center;aspect-ratio:4/5;object-fit:cover;outline:1.5px solid var(--gold);outline-offset:6px}
@media (min-width:860px){.promo{grid-template-columns:1fr 1fr;align-items:center;padding:48px;gap:48px}}

.story{display:grid;gap:24px}
.story img{border-radius:999px 999px 22px 22px;width:100%;max-width:420px;justify-self:center;aspect-ratio:4/5;object-fit:cover;outline:1.5px solid var(--gold);outline-offset:8px}
.story p.muted{margin-top:14px;max-width:52ch}
@media (min-width:860px){.story{grid-template-columns:1fr 1fr;gap:56px;align-items:center}}

.app{background:var(--surface);border:1.5px solid var(--gold);border-radius:26px;padding:28px 22px;display:grid;gap:24px}
.app p.muted{margin:10px 0 20px;max-width:44ch}
.stores{display:flex;gap:10px;flex-wrap:wrap}
.store{display:inline-flex;flex-direction:column;justify-content:center;min-width:150px;min-height:52px;padding:8px 18px;border-radius:14px;background:var(--ink);color:#fff;text-decoration:none;line-height:1.15}
.store small{font-size:.72rem;opacity:.8}
.store b{font-weight:500;font-size:1.1rem}
.store[aria-disabled="true"]{opacity:.45}
.perks{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.perks div{background:rgba(255,255,255,.75);border-radius:16px;padding:14px}
.perks b{display:block;font-weight:500}
.perks span{font-size:.88rem;color:var(--muted)}
@media (min-width:860px){.app{grid-template-columns:1.1fr 1fr;padding:48px;gap:48px;align-items:center}}

.locs{display:grid;gap:12px}
.loc{background:var(--surface);border:1.5px solid var(--line);border-radius:var(--r);padding:20px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:4px}
.loc h3{font-size:1.4rem}
.loc .acts{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}
.loc .acts .btn{min-height:44px;flex:1 1 auto;font-size:.92rem;padding:0 16px}
@media (min-width:760px){.locs{grid-template-columns:1fr 1fr;gap:20px}}

footer{background:var(--night) url(assets/img/wallpaper-dark.svg);background-size:120px 170px;padding-block:28px 36px;font-size:.88rem;color:rgba(255,245,230,.7)}
footer .wrap{display:grid;gap:14px}
footer nav{display:flex;flex-wrap:wrap;gap:4px 18px}
footer nav a{text-decoration:none;padding:6px 0;color:#fff4e2}

/* page titles */
.ptitle{padding-block:28px 8px}
.ptitle p.muted{margin-top:10px;max-width:46ch}
@media (min-width:760px){.ptitle{padding-block:56px 16px}}

/* sticky chips (menu + order) */
.chips{position:sticky;top:calc(var(--hh) + env(safe-area-inset-top,0px));z-index:20;background:rgba(245,236,220,.97);border-bottom:1px solid var(--line)}
.chips .wrap{display:flex;gap:8px;overflow-x:auto;padding-block:10px;scrollbar-width:none}
.chips .wrap::-webkit-scrollbar{display:none}
.chips a{flex:0 0 auto;text-decoration:none;font-weight:500;font-size:.92rem;padding:9px 16px;border-radius:999px;background:var(--soft);color:var(--muted)}
.chips a[aria-current="true"]{background:var(--ink);color:#fff}

/* menu list */
.mlist{max-width:760px;margin:0 auto}
.mgroup{background:var(--surface);border:1.5px solid var(--line);border-radius:22px;padding:22px 18px 6px;margin-top:20px;scroll-margin-top:calc(var(--hh) + 70px)}
.mgroup h2{margin-bottom:6px}
.mgroup h3{font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;font-weight:600;color:var(--olive);margin:22px 0 4px}
.mlist ul{list-style:none;margin:0;padding:0}
.mlist li{display:grid;grid-template-columns:56px minmax(0,1fr) auto;gap:14px;align-items:center;padding:12px 0;border-bottom:1px solid var(--line)}
.mlist li img{width:56px;height:56px;border-radius:14px;object-fit:cover}
.mlist .n{font-size:1.08rem;line-height:1.3}
.mlist small{display:block;color:var(--muted);font-size:.86rem;line-height:1.35}
.mlist .p{font-weight:500;font-variant-numeric:tabular-nums}
.note{font-size:.85rem;color:var(--muted);text-align:center;margin:28px auto 0;max-width:52ch}

/* order */
.demo{background:var(--olive-soft);color:var(--ink);font-size:.86rem;text-align:center;padding:9px 16px}
.demo b{font-weight:600}
.setup{display:grid;gap:12px;margin-top:18px}
.seg{display:grid;grid-template-columns:1fr 1fr;gap:6px;background:var(--soft);padding:5px;border-radius:16px}
.seg button{border:0;background:none;border-radius:12px;padding:10px 8px;cursor:pointer;text-align:left;min-height:56px}
.seg button b{display:block;font-weight:500;font-size:.98rem}
.seg button span{font-size:.78rem;color:var(--muted)}
.seg button[aria-pressed="true"]{background:var(--surface);box-shadow:var(--shadow)}
.field{display:flex;flex-direction:column;gap:6px;font-size:.85rem;color:var(--muted)}
select,input,textarea{font:inherit;font-size:16px;color:var(--ink);background:var(--surface);border:1.5px solid var(--line);border-radius:12px;padding:12px 14px;min-height:48px;width:100%}
select:focus,input:focus,textarea:focus{outline:none;border-color:var(--olive)}
@media (min-width:760px){.setup{grid-template-columns:1.6fr 1fr;align-items:end}}
.olayout{display:grid;gap:32px;padding-bottom:32px}
@media (min-width:1000px){.olayout{grid-template-columns:minmax(0,1fr) 360px;align-items:start}}
.osec{padding-top:24px}
.osec h2{font-size:1.5rem;font-weight:400;margin-bottom:10px}
.ogrid{display:grid;gap:10px}
@media (min-width:640px){.ogrid{grid-template-columns:1fr 1fr}}
.oitem{display:grid;grid-template-columns:minmax(0,1fr) 96px;gap:14px;align-items:center;background:var(--surface);border:0;border-radius:var(--r);padding:12px 12px 12px 16px;text-align:left;cursor:pointer;box-shadow:var(--shadow);width:100%}
.oitem .n{font-size:1.04rem;line-height:1.3;display:block}
.oitem small{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;color:var(--muted);font-size:.84rem;line-height:1.35;margin-top:2px}
.oitem .p{display:block;margin-top:6px;font-weight:500}
.oitem .ph{position:relative}
.oitem img{width:96px;height:96px;border-radius:14px;object-fit:cover}
.oitem .plus{position:absolute;right:-4px;bottom:-4px;width:34px;height:34px;border-radius:50%;background:var(--surface);box-shadow:var(--shadow);display:grid;place-items:center;font-size:1.4rem;line-height:1}
.oitem .qtyb{position:absolute;left:-6px;top:-6px;min-width:26px;height:26px;border-radius:999px;background:var(--olive);color:#fff;font-size:.8rem;font-weight:600;display:grid;place-items:center;padding:0 7px}

/* cart: sidebar on desktop, bottom sheet on phones */
.cart{background:var(--surface);border-radius:22px;box-shadow:var(--shadow);display:flex;flex-direction:column;overflow:hidden}
.cart header{display:flex;justify-content:space-between;align-items:center;padding:18px 20px 12px}
.cart header h2{font-size:1.4rem;font-weight:400}
.cart .x{border:0;background:var(--soft);border-radius:999px;min-width:40px;height:40px;cursor:pointer;font-size:1.1rem}
.cart .body{padding:0 20px;overflow:auto;flex:1}
.cart .foot{padding:14px 20px 20px;border-top:1px solid var(--line)}
.cline{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;padding:12px 0;border-bottom:1px solid var(--line)}
.cline b{font-weight:500}
.cline small{color:var(--muted);font-size:.82rem;grid-column:1}
.step{display:inline-flex;align-items:center;gap:2px;background:var(--soft);border-radius:999px;margin-top:6px;width:max-content}
.step button{border:0;background:none;width:36px;height:34px;cursor:pointer;font-size:1.1rem}
.step span{min-width:18px;text-align:center;font-size:.92rem}
.sum{display:grid;grid-template-columns:1fr auto;gap:4px;font-size:.92rem;color:var(--muted);margin-bottom:14px}
.sum b{color:var(--ink);font-weight:600;font-size:1.05rem}
.empty{color:var(--muted);text-align:center;padding:28px 0}
.form{display:grid;gap:12px;padding-bottom:6px}
.paybox{border:1.5px dashed var(--line);border-radius:14px;padding:14px;font-size:.85rem;color:var(--muted)}
.paybox .row{display:grid;grid-template-columns:1fr 90px;gap:8px;margin-top:8px}
.done{text-align:center;padding:12px 0 6px}
.done .tick{width:64px;height:64px;border-radius:50%;background:var(--olive);color:#fff;display:grid;place-items:center;margin:4px auto 14px;font-size:1.8rem}
.done h3{font-size:1.5rem;margin-bottom:6px}
.back{border:0;background:none;color:var(--olive);font-weight:500;cursor:pointer;padding:8px 0}
@media (min-width:1000px){.cart{position:sticky;top:calc(var(--hh) + 80px);max-height:calc(100vh - var(--hh) - 100px)}.cart .x{display:none}.cartbar{display:none!important}}
@media (max-width:999px){
  .cart{position:fixed;left:0;right:0;bottom:0;z-index:60;border-radius:22px 22px 0 0;max-height:min(88vh,calc(100% - 40px));transform:translateY(105%);transition:transform .28s cubic-bezier(.2,.8,.2,1);padding-bottom:var(--safe-b);visibility:hidden}
  .cart.open{transform:none;visibility:visible}
}
.cartbar{position:fixed;left:12px;right:12px;bottom:calc(var(--tab) + var(--safe-b) + 10px);z-index:35;display:flex;align-items:center;justify-content:space-between;gap:10px;
  background:var(--ink);color:#fff;border:0;border-radius:16px;min-height:56px;padding:0 18px;cursor:pointer;box-shadow:0 10px 30px rgba(0,0,0,.25);font-weight:500}
.cartbar .ct{background:rgba(255,255,255,.16);border-radius:999px;padding:3px 10px;font-size:.85rem}
.has-cartbar{padding-bottom:calc(var(--tab) + var(--safe-b) + 80px)}
.toast{position:fixed;left:50%;bottom:calc(var(--tab) + var(--safe-b) + 78px);transform:translateX(-50%);z-index:80;white-space:nowrap;}
@media (min-width:1000px){.toast{bottom:28px}}
.scrim{position:fixed;inset:0;z-index:55;background:rgba(20,18,14,.45)}

/* item sheet (order) and quick view (menu) */
.sheet{position:fixed;inset:0;z-index:70;display:flex;align-items:flex-end;justify-content:center;background:rgba(20,18,14,.5)}
.sheet .box{background:var(--surface);width:100%;max-width:520px;max-height:92vh;border-radius:24px 24px 0 0;overflow:auto;padding-bottom:var(--safe-b);animation:up .25s cubic-bezier(.2,.8,.2,1);display:flex;flex-direction:column}
.sheet .box>img{width:100%;aspect-ratio:16/11;object-fit:cover;flex:none}
.sheet .in{padding:18px 20px 8px}
.sheet h3{font-size:1.6rem}
.sheet .price{font-weight:500;font-size:1.1rem;margin-top:4px}
.sheet .desc{color:var(--muted);margin-top:8px}
.sheet fieldset{border:0;padding:0;margin:18px 0 0}
.sheet legend{font-weight:600;font-size:.9rem;margin-bottom:8px}
.opts{display:flex;flex-wrap:wrap;gap:8px}
.opts label{position:relative}
.opts input{position:absolute;opacity:0;width:1px;height:1px;min-height:0}
.opts span{display:block;padding:10px 16px;border-radius:999px;border:1.5px solid var(--line);font-size:.92rem;cursor:pointer}
.opts input:checked+span{border-color:var(--ink);background:var(--ink);color:#fff}
.opts input:focus-visible+span{outline:2.5px solid var(--olive);outline-offset:2px}
.sheet .bar{position:sticky;bottom:0;background:var(--surface);display:flex;gap:10px;align-items:center;padding:14px 20px 16px;border-top:1px solid var(--line);margin-top:auto}
.sheet .bar .step{margin:0}
.sheet .bar .btn{flex:1}
.sheet .close{position:absolute;margin:12px;width:40px;height:40px;border-radius:50%;border:0;background:rgba(255,255,255,.92);cursor:pointer;font-size:1.1rem;box-shadow:var(--shadow);z-index:1}
@media (min-width:600px){.sheet{align-items:center;padding:24px}.sheet .box{border-radius:24px;max-height:88vh}}
@keyframes up{from{transform:translateY(40px);opacity:.5}}

/* visit */
.loc-tabs{display:grid;grid-template-columns:1fr 1fr;gap:6px;background:var(--soft);padding:5px;border-radius:16px;margin:18px 0 14px}
.loc-tab{border:0;background:none;border-radius:12px;padding:10px 12px;text-align:left;cursor:pointer;min-height:56px}
.loc-tab b{display:block;font-weight:500}
.loc-tab span{font-size:.78rem;color:var(--muted)}
.loc-tab[aria-selected="true"]{background:var(--surface);box-shadow:var(--shadow)}
.bigmap{position:relative;height:min(62vh,560px);min-height:320px;border-radius:22px 22px 0 0;overflow:hidden;background:var(--soft)}
.bigmap iframe,.bigmap .map-fallback{position:absolute;inset:0;width:100%;height:100%;border:0}
.bigmap .map-fallback img{width:100%;height:100%;object-fit:cover;opacity:.35}
.bigmap .map-fallback span{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);background:var(--surface);padding:10px 16px;border-radius:12px;font-size:.88rem;text-align:center;max-width:80%;box-shadow:var(--shadow)}
.mapbar{display:grid;gap:14px;background:var(--surface);padding:20px;border-radius:0 0 22px 22px;box-shadow:var(--shadow)}
.mapbar h3{font-size:1.35rem}
.mapbar .acts{display:grid;grid-template-columns:1fr 1fr;gap:8px}
@media (min-width:760px){.mapbar{grid-template-columns:1fr auto;align-items:center;padding:24px 28px}.mapbar .acts{display:flex}}
.strip{display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;margin:0 -16px;padding:0 16px 6px;scrollbar-width:none}
.strip img{flex:0 0 auto;width:min(260px,64vw);aspect-ratio:4/5;object-fit:cover;border-radius:18px;scroll-snap-align:start}
/* closest cafe */
.near{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;margin:4px 0 14px}
.nearbtn{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 18px;border-radius:999px;border:1.5px solid var(--gold);background:var(--surface);color:var(--ink);font-weight:500;cursor:pointer}
.nearbtn svg{width:18px;height:18px;fill:none;stroke:var(--rose);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.nearbtn[disabled]{opacity:.6}
.near-out{font-size:.92rem;color:var(--muted)}
.near-out b{color:var(--ink);font-weight:500}
.loc.is-near{border-color:var(--gold);order:-1}
.loc.is-near::before,.loc-tab.is-near b::after,.seg button.is-near b::after{content:"Closest to you";display:inline-block;font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;font-weight:600;color:#fff;background:var(--rose);border-radius:999px;padding:3px 9px;vertical-align:middle}
.loc.is-near::before{align-self:flex-start;margin-bottom:6px}
.loc-tab.is-near b::after,.seg button.is-near b::after{content:"Closest";margin-left:6px;font-size:.58rem;padding:2px 7px}
/* ornaments */
.band{height:30px;background:var(--night) url(assets/img/border.svg) repeat-x center/auto 30px}
.head h2::before,.ptitle h1::before,.mgroup h2::before,.osec h2::before{content:"";display:block;width:96px;height:18px;background:url(assets/img/orn.svg) no-repeat left center/contain;margin-bottom:10px}
.mgroup h2::before{margin-inline:0}
.ptitle h1::before{width:120px;height:22px}
.panel{background:var(--surface);border:1.5px solid var(--line);border-radius:22px;padding:8px 18px 18px}
/* full-screen landing photo */
.fhero{position:relative;height:calc(100svh - var(--tab) - var(--safe-b));min-height:540px;max-height:1100px;color:#fff;display:flex;align-items:flex-end;overflow:hidden;background:var(--night);isolation:isolate}
.fhero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:36% center;z-index:-2}
.fhero::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,rgba(24,14,6,.6) 0%,rgba(24,14,6,.08) 28%,rgba(24,14,6,.3) 52%,rgba(24,14,6,.9) 100%)}
.fhero .frame{position:absolute;inset:calc(var(--hh) + env(safe-area-inset-top,0px) + 8px) 12px 12px;border:1.5px solid rgba(225,195,125,.75);border-radius:50% 50% 12px 12px/110px 110px 12px 12px;pointer-events:none}
.fhero .frame::before{content:"";position:absolute;inset:6px;border:1px solid rgba(225,195,125,.4);border-radius:inherit}
.fh-in{position:relative;text-align:center;padding-bottom:44px;width:100%}
.fh-in .orn-l{display:block;width:150px;height:26px;margin:0 auto 14px;background:url(assets/img/orn-light.svg) no-repeat center/contain}
.fh-in .eyebrow{color:#e9cf8f}
.fh-in h1{font-size:clamp(3.6rem,17vw,8.5rem);font-weight:300;letter-spacing:-.01em;line-height:.95}
.fh-in .lede{font-size:1.08rem;max-width:34ch;margin:14px auto 24px;opacity:.92}
.fh-in .ctas{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.fh-in .btn{background:#fff7e8;color:var(--ink);min-width:150px}
.fh-in .btn.line{background:rgba(255,255,255,.08);color:#fff;box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.75);backdrop-filter:blur(4px)}
@media (min-width:900px){.fhero .frame{inset:calc(var(--hh) + 16px) 24px 24px;border-radius:50% 50% 14px 14px/190px 190px 14px 14px}.fh-in{padding-bottom:80px}}
.top.over{position:fixed;left:0;right:0;transition:background .3s,border-color .3s}
.top.over:not(.solid){background:transparent;border-color:transparent;backdrop-filter:none;-webkit-backdrop-filter:none;color:#fff}
.top.over:not(.solid) .brand small,.top.over:not(.solid) .nav a{color:rgba(255,255,255,.85)}
.top.over:not(.solid) .nav a[aria-current]{background:rgba(255,255,255,.14);color:#fff}
.top.over:not(.solid) .btn{background:#fff7e8;color:var(--ink)}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

JS = r"""
const miles=(a,b,c,d)=>{const r=x=>x*Math.PI/180,h=Math.sin(r(c-a)/2)**2+Math.cos(r(a))*Math.cos(r(c))*Math.sin(r(d-b)/2)**2;return 7917.6*Math.asin(Math.sqrt(h))};
function applyNear(id,user){document.querySelectorAll('[data-loc-id]').forEach(el=>el.classList.toggle('is-near',el.dataset.locId===id));document.dispatchEvent(new CustomEvent('nearest',{detail:{id,user}}))}
document.querySelectorAll('[data-near]').forEach(box=>{const btn=box.querySelector('button'),out=box.querySelector('.near-out');
  btn.addEventListener('click',()=>{
    if(!navigator.geolocation){out.textContent='Location isn\u2019t available in this browser.';return}
    btn.disabled=true;out.textContent='Finding the closest cafe\u2026';
    navigator.geolocation.getCurrentPosition(p=>{btn.disabled=false;const {latitude:a,longitude:b}=p.coords;
      const n=LOCS.map(L=>({...L,d:miles(a,b,L.lat,L.lng)})).sort((x,y)=>x.d-y.d)[0];
      out.innerHTML=`Closest to you: <b>Misree Chai ${n.name}</b>, about ${n.d<10?n.d.toFixed(1):Math.round(n.d)} mi away.`;
      try{localStorage.setItem('misree-near',n.id)}catch(e){}
      applyNear(n.id,true)},
    e=>{btn.disabled=false;out.textContent=e.code===1?'Location is off, so pick a cafe below.':'Couldn\u2019t get your location, so pick a cafe below.'},{timeout:10000,maximumAge:600000})})});
setTimeout(()=>{let id;try{id=localStorage.getItem('misree-near')}catch(e){}const L=LOCS.find(x=>x.id===id);if(!L)return;
  document.querySelectorAll('[data-near] .near-out').forEach(o=>o.innerHTML=`Your closest cafe: <b>Misree Chai ${L.name}</b>`);applyNear(id)});
const over=document.querySelector('.top.over');
if(over){const f=()=>over.classList.toggle('solid',scrollY>40);addEventListener('scroll',f,{passive:true});f()}
// menu + order chips scrollspy
const chips=document.querySelectorAll('.chips a');
if(chips.length){
  const map=new Map([...chips].map(a=>[a.getAttribute('href').slice(1),a]));
  const spy=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){chips.forEach(t=>t.removeAttribute('aria-current'));const a=map.get(e.target.id);
    if(a){a.setAttribute('aria-current','true');const w=a.parentElement;w.scrollTo({left:a.offsetLeft-w.clientWidth/2+a.clientWidth/2,behavior:'smooth'})}}}),{rootMargin:'-30% 0px -60% 0px'});
  document.querySelectorAll('[data-sec]').forEach(s=>spy.observe(s));
}
// visit page location switcher
const ltabs=document.querySelectorAll('.loc-tab');
ltabs.forEach(t=>t.addEventListener('click',()=>{const d=t.dataset;ltabs.forEach(x=>x.setAttribute('aria-selected',x===t));
  document.getElementById('loc-map').src=d.embed;document.getElementById('loc-dir').href=d.dir;
  document.getElementById('loc-order').href='order.html?store='+d.loc;
  document.getElementById('loc-name').textContent='Misree Chai · '+d.name;
  document.getElementById('loc-l1').textContent=d.l1+', '+d.l2;
  document.getElementById('loc-meta').textContent=d.phone?'Open daily · '+d.phone:'Open daily · check hours on Google Maps';}));
document.addEventListener('nearest',e=>{const t=document.querySelector('.loc-tab[data-loc-id="'+e.detail.id+'"]');if(t&&t.getAttribute('aria-selected')!=='true')t.click()});
// menu quick view
const qv=document.getElementById('qv');
if(qv){
  let last=null;const close=()=>{qv.hidden=true;document.body.style.overflow='';last&&last.focus()};
  document.querySelectorAll('[data-qv]').forEach(c=>c.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();c.click()}}));
  document.querySelectorAll('[data-qv]').forEach(c=>c.addEventListener('click',()=>{last=c;const d=c.dataset;
    qv.querySelector('img').src=d.img;qv.querySelector('h3').textContent=d.title;qv.querySelector('.price').textContent=d.price;
    qv.querySelector('.desc').textContent=d.desc||'';qv.hidden=false;document.body.style.overflow='hidden';qv.querySelector('.close').focus()}));
  qv.addEventListener('click',e=>{if(e.target===qv)close()});qv.querySelector('.close').addEventListener('click',close);
  addEventListener('keydown',e=>{if(e.key==='Escape'&&!qv.hidden)close()});
}
"""

# Demo ordering: everything stays in the browser. Nothing is sent or charged.
ORDER_JS = r"""
const D=JSON.parse(document.getElementById('menu-data').textContent);
const ITEMS=new Map(D.items.map(i=>[i.id,i]));
const $=s=>document.querySelector(s);
const money=n=>'$'+n.toFixed(2);
const state={store:D.stores[0].id,cart:[],view:'cart'};
let want=new URLSearchParams(location.search).get('store');if(!want)try{want=localStorage.getItem('misree-near')}catch(e){}
if(D.stores.some(s=>s.id===want))state.store=want;
const store=()=>D.stores.find(s=>s.id===state.store);
const segs=document.querySelectorAll('.seg button');
const setStore=id=>{state.store=id;segs.forEach(b=>b.setAttribute('aria-pressed',b.dataset.store===id));render()};
segs.forEach(b=>b.addEventListener('click',()=>setStore(b.dataset.store)));
// pickup times: ASAP plus 15 minute slots for the next 3 hours
const sel=$('#pickup');const now=new Date();now.setMinutes(Math.ceil((now.getMinutes()+20)/15)*15,0,0);
for(let i=0;i<12;i++){const t=new Date(now.getTime()+i*9e5);const o=document.createElement('option');o.textContent=t.toLocaleTimeString([],{hour:'numeric',minute:'2-digit'});sel.append(o)}
// item sheet
const sheet=$('#sheet');let cur=null,qty=1,lastBtn=null;
const lineTotal=()=>cur?cur.price*qty:0;
const sync=()=>{$('#s-qty').textContent=qty;$('#s-add').textContent='Add '+qty+' to order · '+money(lineTotal())};
function openItem(id,btn){cur=ITEMS.get(id);qty=1;lastBtn=btn;
  sheet.querySelector('img').src=cur.img;sheet.querySelector('img').alt=cur.name;$('#s-name').textContent=cur.name;$('#s-price').textContent=money(cur.price);
  $('#s-desc').textContent=cur.desc;$('#s-desc').hidden=!cur.desc;
  $('#s-opts').innerHTML=cur.opts.map((g,gi)=>`<fieldset><legend>${g[0]}</legend><div class="opts">${g[1].map((o,oi)=>`<label><input type="radio" name="o${gi}" value="${o}"${oi?'':' checked'}><span>${o}</span></label>`).join('')}</div></fieldset>`).join('');
  $('#s-note').value='';sync();sheet.hidden=false;document.body.style.overflow='hidden';sheet.querySelector('.close').focus()}
function closeItem(){sheet.hidden=true;if(!cartOpen())document.body.style.overflow='';lastBtn&&lastBtn.focus()}
document.querySelectorAll('[data-add]').forEach(b=>b.addEventListener('click',()=>openItem(b.dataset.add,b)));
sheet.addEventListener('click',e=>{if(e.target===sheet)closeItem()});sheet.querySelector('.close').addEventListener('click',closeItem);
$('#s-minus').addEventListener('click',()=>{qty=Math.max(1,qty-1);sync()});$('#s-plus').addEventListener('click',()=>{qty=Math.min(20,qty+1);sync()});
$('#s-add').addEventListener('click',()=>{
  const opts=[...sheet.querySelectorAll('input[type=radio]:checked')].map(i=>i.value).filter(v=>!/^Regular/.test(v));
  const note=$('#s-note').value.trim();const key=cur.id+'|'+opts.join(',')+'|'+note;
  const hit=state.cart.find(l=>l.key===key);if(hit)hit.qty+=qty;else state.cart.push({key,id:cur.id,qty,opts,note});
  state.view='cart';closeItem();render();toast(cur.name+' added')});
// cart
const cart=$('#cart'),scrim=$('#scrim'),bar=$('#cartbar');
const cartOpen=()=>cart.classList.contains('open');
const openCart=()=>{cart.classList.add('open');scrim.hidden=false;document.body.style.overflow='hidden';cart.querySelector('.x').focus()};
const closeCart=()=>{cart.classList.remove('open');scrim.hidden=true;document.body.style.overflow='';bar.focus()};
bar.addEventListener('click',openCart);scrim.addEventListener('click',closeCart);cart.querySelector('.x').addEventListener('click',closeCart);
addEventListener('keydown',e=>{if(e.key!=='Escape')return;if(!sheet.hidden)closeItem();else if(cartOpen())closeCart()});
const totals=()=>{const sub=state.cart.reduce((s,l)=>s+ITEMS.get(l.id).price*l.qty,0);const tax=Math.round(sub*store().tax*100)/100;return{sub,tax,total:sub+tax,count:state.cart.reduce((s,l)=>s+l.qty,0)}};
function render(){
  const t=totals(),body=$('#c-body'),foot=$('#c-foot'),s=store();
  document.querySelectorAll('[data-add]').forEach(b=>{const n=state.cart.filter(l=>l.id===b.dataset.add).reduce((a,l)=>a+l.qty,0);const q=b.querySelector('.qtyb');q.hidden=!n;q.textContent=n});
  bar.hidden=!t.count||state.view==='done';document.body.classList.toggle('has-cartbar',!bar.hidden);
  $('#cb-count').textContent=t.count+(t.count===1?' item':' items');$('#cb-total').textContent=money(t.total);
  $('#c-title').textContent=state.view==='checkout'?'Checkout':state.view==='done'?'Order placed':'Your order';
  if(state.view==='done'){body.innerHTML=`<div class="done"><div class="tick" aria-hidden="true">✓</div><h3>Thanks, ${esc(state.name)}!</h3>
    <p class="muted">Order #${state.no} for pickup at Misree Chai ${s.name}, ${s.line1}. Ready ${esc(state.time)}.</p>
    <p class="muted" style="margin-top:12px;font-size:.85rem">This is a demo, so no order was sent and no card was charged.</p></div>`;
    foot.innerHTML='<button class="btn block" type="button" id="c-new">Start a new order</button>';
    $('#c-new').onclick=()=>{state.cart=[];state.view='cart';render();if(cartOpen())closeCart()};return}
  if(!state.cart.length){body.innerHTML='<p class="empty">Your bag is empty.<br>Tap any item to add it.</p>';foot.innerHTML='';state.view='cart';return}
  const sum=`<div class="sum"><span>Subtotal</span><span>${money(t.sub)}</span><span>Est. tax</span><span>${money(t.tax)}</span><b>Total</b><b>${money(t.total)}</b></div>`;
  if(state.view==='checkout'){
    body.innerHTML=`<button class="back" type="button" id="c-back">← Back to order</button>
    <p class="muted" style="font-size:.88rem;margin-bottom:12px">Pickup at <b style="color:var(--ink);font-weight:500">${s.name}</b>, ${s.line1} · ${esc(sel.value)}</p>
    <form class="form" id="c-form" novalidate><label class="field">Name<input name="name" autocomplete="given-name" required placeholder="Your name"></label>
    <label class="field">Phone, for a text when it's ready<input name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="(555) 555-0123"></label>
    <div class="paybox">Payment (demo, nothing is charged)<input aria-label="Card number" inputmode="numeric" placeholder="Card number" style="margin-top:8px"><div class="row"><input aria-label="Expiry" placeholder="MM / YY" inputmode="numeric"><input aria-label="CVC" placeholder="CVC" inputmode="numeric"></div></div></form>`;
    foot.innerHTML=sum+`<button class="btn block olive" type="submit" form="c-form">Place order · ${money(t.total)}</button>`;
    $('#c-back').onclick=()=>{state.view='cart';render()};
    $('#c-form').addEventListener('submit',e=>{e.preventDefault();const n=e.target.name;if(!n.value.trim()){n.focus();n.style.borderColor='#b3261e';return}
      state.name=n.value.trim();state.no=1000+Math.floor(Math.random()*9000);state.time=sel.selectedIndex?'at '+sel.value:'in about 15 minutes';state.view='done';render();
      cart.scrollIntoView({block:'nearest'})});return}
  body.innerHTML=state.cart.map((l,i)=>{const it=ITEMS.get(l.id);const extra=[...l.opts,l.note&&('“'+esc(l.note)+'”')].filter(Boolean).join(' · ');
    return `<div class="cline"><b>${it.name}</b><span>${money(it.price*l.qty)}</span>${extra?`<small>${extra}</small>`:''}
    <div class="step" style="grid-column:1"><button type="button" aria-label="Remove one" data-dec="${i}">${l.qty>1?'−':'×'}</button><span>${l.qty}</span><button type="button" aria-label="Add one" data-inc="${i}">+</button></div></div>`}).join('');
  foot.innerHTML=sum+`<button class="btn block" type="button" id="c-go">Checkout</button>`;
  body.querySelectorAll('[data-inc]').forEach(b=>b.onclick=()=>{state.cart[b.dataset.inc].qty++;render()});
  body.querySelectorAll('[data-dec]').forEach(b=>b.onclick=()=>{const l=state.cart[b.dataset.dec];if(--l.qty<1)state.cart.splice(b.dataset.dec,1);render();if(!state.cart.length&&cartOpen())closeCart()});
  $('#c-go').onclick=()=>{state.view='checkout';render()};
}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
let tt;function toast(m){const el=$('#toast');el.textContent=m;el.hidden=false;clearTimeout(tt);tt=setTimeout(()=>el.hidden=true,1600)}
setStore(state.store);
let fromUrl=new URLSearchParams(location.search).has('store');
document.addEventListener('nearest',e=>{if(e.detail.user||!fromUrl)setStore(e.detail.id)});
"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600&display=swap">'

def page(title, desc, body, is_index=False, extra_js=""):
    head = (f'<title>{title}</title><meta name="claude:viewport-fit-sides" content="cover"><meta name="theme-color" content="#fbf8f3">'
            f'<meta name="description" content="{esc(desc)}"><meta property="og:image" content="{img("chai-cheers")}"><link rel="icon" href="assets/img/logo.png">{FONTS}<style>{CSS}</style>')
    locs = json.dumps([dict(id=L['id'], name=L['name'], lat=L['lat'], lng=L['lng']) for L in LOCATIONS])
    tail = f'<script>const LOCS={locs};{JS}{extra_js}</script>'
    if ARTIFACT and is_index:
        return head + body + tail
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'{head}</head><body>{body}{tail}</body></html>')

ICONS = {
    "home": '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
    "menu": '<path d="M5 4h14v16H5z"/><path d="M9 9h6M9 13h6M9 17h3"/>',
    "order": '<path d="M5 8h14l-1 12H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "rewards": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    "visit": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
}
NAV = [("home", "Home", "index.html"), ("menu", "Menu", "menu.html"), ("order", "Order", "order.html"),
       ("rewards", "Rewards", "index.html#rewards"), ("visit", "Visit", "visit.html")]

def header(current="home", over=False):
    cur = lambda k: ' aria-current="page"' if k == current else ""
    links = "".join(f'<a href="{h}"{cur(k)}>{"Join our Rewards Program" if k == "rewards" else ("Order Online" if k == "order" else t)}</a>'
                    for k, t, h in NAV if k != "order")
    tabs = "".join(f'<a href="{h}"{cur(k)}{" class=order" if k == "order" else ""}>'
                   f'{"<span>" if k == "order" else ""}<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[k]}</svg>{"</span>" if k == "order" else ""}{t}</a>' for k, t, h in NAV)
    order_btn = f'<a class="btn" href="order.html"{cur("order")}>Order Online</a>'
    return (f'<header class="top{' over' if over else ''}"><div class="wrap"><a class="brand" href="index.html" aria-label="Misree Chai home"><img src="assets/img/logo.png" alt="" width="36" height="36">misree <small>chai</small></a>'
            f'<nav class="nav" aria-label="Main">{links}</nav>{order_btn}</div></header>'
            f'<nav class="tabbar" aria-label="Main">{tabs}</nav>')

def footer():
    return (f'<div class="band" aria-hidden="true"></div><footer><div class="wrap"><nav aria-label="More"><a href="menu.html">Menu</a><a href="order.html">Order for pickup</a><a href="visit.html">Visit</a>'
            f'<a href="{INSTA}" target="_blank" rel="noopener">Instagram</a><a href="{DOORDASH}" target="_blank" rel="noopener">DoorDash</a><a href="{UBER}" target="_blank" rel="noopener">Uber Eats</a></nav>'
            f'<p>Misree Chai · Jersey City &amp; Jackson Heights. Prices are from the cafe\'s online ordering menu and may change. Photos are styled representations.</p></div></footer>')

def near_box():
    return ('<div class="near" data-near><button class="nearbtn" type="button"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/><circle cx="12" cy="12" r="7"/></svg>Find my closest cafe</button>'
            '<p class="near-out" role="status" aria-live="polite"></p></div>')

def loc_cards():
    def card(L):
        meta = f'Open daily · {L["phone"]}' if L["phone"] else "Open daily"
        return (f'<div class="loc" data-loc-id="{L["id"]}"><p class="eyebrow" style="margin:0">{L["name"]}</p><h3>{L["line1"]}</h3><p class="muted">{L["line2"]}</p><p class="muted">{meta}</p>'
                f'<div class="acts"><a class="btn" href="order.html?store={L["id"]}">Order pickup</a><a class="btn line" href="{L["dir"]}" target="_blank" rel="noopener">Directions</a></div></div>')
    return f'<div class="locs">{"".join(card(L) for L in LOCATIONS)}</div>'

def build_index():
    cats = "".join(f'<a class="cat" href="menu.html#{c["slug"]}"><img src="{sm(c["items"][0][2])}" alt="" loading="lazy" width="520" height="391"><b>{c["name"]}</b><span>{len(c["items"])} items</span></a>' for c in CATS)
    picks_src = [("kulfi", 0), ("chai", 0), ("crepes", 0), ("bowls", 0)]
    picks = "".join((lambda n, p, im, d: f'<a class="pick" href="order.html"><img src="{sm(im)}" alt="" loading="lazy" width="520" height="391"><div><b>{n}</b><span>${p}</span></div></a>')(*BYSLUG[s]["items"][i]) for s, i in picks_src)
    body = f'''{header("home", over=True)}
<main>
<section class="fhero"><img src="{img("chai-pour")}" alt="Chai being poured into small glasses" width="1400" height="1054" fetchpriority="high"><div class="frame" aria-hidden="true"></div>
<div class="wrap fh-in"><span class="orn-l" aria-hidden="true"></span><p class="eyebrow">Jersey City · Jackson Heights</p><h1>Misree Chai</h1>
<p class="lede">Masala chai, kulfi milk tea, sweet crepes and acai bowls, made fresh at both of our cafes.</p>
<div class="ctas"><a class="btn" href="order.html">Order pickup</a><a class="btn line" href="menu.html">View menu</a></div></div></section>
<div class="band" aria-hidden="true"></div>
<section style="padding-block:44px 40px"><div class="wrap"><div class="head"><h2>The menu</h2><a href="menu.html">See all →</a></div><div class="cats">{cats}</div></div></section>
<section class="pad" style="padding-top:8px"><div class="wrap"><div class="head"><h2>From the menu</h2><a href="order.html">Order →</a></div><div class="picks">{picks}</div></div></section>
<section style="padding-bottom:48px"><div class="wrap"><div class="promo"><div><p class="eyebrow">Order online</p><h2>Skip the line.</h2>
<p class="muted">Order ahead and pick it up at Jersey City or Jackson Heights. We'll have it ready when you walk in.</p><a class="btn" href="order.html">Start an order</a></div>
<img src="{sm("falooda-kulfi")}" alt="" loading="lazy" width="520" height="391"></div></div></section>
<section class="pad"><div class="wrap story"><img src="{sm("misri")}" alt="Misri rock sugar beside a glass of chai" loading="lazy" width="520" height="391">
<div><p class="eyebrow">Why "Misree"</p><h2>Named for the sugar that sweetens the cup.</h2>
<p class="muted">Misri is crystallized rock sugar, stirred into chai and passed around after meals across South Asia. Misree Chai brings that ritual to Jersey City and Jackson Heights, alongside the milk teas, crepes and bowls our neighbors keep coming back for.</p></div></div></section>
<section class="pad" id="rewards" style="scroll-margin-top:var(--hh)"><div class="wrap"><div class="app"><div><p class="eyebrow">The Misree Chai app</p><h2>Join our Rewards Program.</h2>
<p class="muted">Download the Misree Chai app to order ahead, collect rewards on every visit, and hear about new drinks first.</p>
<div class="stores">{store_btn(APP_STORE, "Download on the", "App Store")}{store_btn(PLAY_STORE, "Get it on", "Google Play")}</div></div>
<div class="perks"><div><b>Order ahead</b><span>Skip the line</span></div><div><b>Earn rewards</b><span>On every visit</span></div><div><b>New drinks</b><span>Hear first</span></div><div><b>Both cafes</b><span>NJ &amp; Queens</span></div></div></div></div></section>
<section class="pad" style="padding-top:0"><div class="wrap"><div class="head"><h2>Visit us</h2><a href="visit.html">Map →</a></div>{near_box()}{loc_cards()}</div></section>
</main>{footer()}'''
    return page("Misree Chai", "Misree Chai: chai, kulfi milk tea, crepes and bowls in Jersey City and Jackson Heights. Order online for pickup.", body, True)

QV = '''<div class="sheet" id="qv" hidden role="dialog" aria-modal="true" aria-labelledby="qv-t"><div class="box" style="position:relative"><button class="close" type="button" aria-label="Close">✕</button><img src="" alt="">
<div class="in"><h3 id="qv-t"></h3><p class="price"></p><p class="desc"></p></div><div class="bar"><a class="btn block" href="order.html">Order for pickup</a></div></div></div>'''

def build_menu():
    chips = "".join(f'<a href="#{g}">{name}</a>' for g, name, _ in GROUPS)
    secs = ""
    for g, name, slugs in GROUPS:
        lists = ""
        for sl in slugs:
            c = BYSLUG[sl]
            sub = f'<h3 id="{sl}">{c["name"]}</h3>' if len(slugs) > 1 else ""
            rows = "".join(f'<li data-qv data-title="{esc(n)}" data-price="${p}" data-img="{img(im)}" data-desc="{esc(d)}" role="button" tabindex="0" style="cursor:pointer">'
                           f'<img src="{sm(im)}" alt="" loading="lazy" width="56" height="56"><span><span class="n">{n}</span>{f"<small>{d}</small>" if d else ""}</span><span class="p">${p}</span></li>'
                           for n, p, im, d in c["items"])
            lists += f'{sub}<ul>{rows}</ul>'
        secs += f'<section class="mgroup" id="{g}" data-sec><h2>{name}</h2>{lists}</section>'
    body = f'''{header("menu")}<main>
<div class="wrap ptitle"><p class="eyebrow">Served at both cafes</p><h1>Menu</h1></div>
<nav class="chips" aria-label="Menu sections"><div class="wrap">{chips}</div></nav>
<div class="wrap"><div class="mlist">{secs}
<p class="note">Tap an item to see a photo. Prices are from the cafe's online ordering menu and may differ in store.</p>
<div style="display:flex;justify-content:center;margin:24px 0 48px"><a class="btn" href="order.html">Order for pickup</a></div></div></div></main>
{footer()}{QV}'''
    return page("Menu · Misree Chai", "The full Misree Chai menu: drinks, crepes, bowls and bakery.", body)

def build_order():
    items = []
    secs = ""
    for c in CATS:
        cards = ""
        for n, p, im, d in c["items"]:
            iid = slug(n)
            items.append(dict(id=iid, name=n, price=float(p), img=img(im), desc=d, opts=OPTIONS[c["opts"]]))
            cards += (f'<button class="oitem" type="button" data-add="{iid}" aria-label="{esc(n)}, ${p}"><span><span class="n">{n}</span>{f"<small>{d}</small>" if d else ""}<span class="p">${p}</span></span>'
                      f'<span class="ph"><img src="{sm(im)}" alt="" loading="lazy" width="96" height="96"><span class="plus" aria-hidden="true">+</span><span class="qtyb" hidden></span></span></button>')
        secs += f'<section class="osec" id="o-{c["slug"]}" data-sec><h2>{c["name"]}</h2><div class="ogrid">{cards}</div></section>'
    stores = [dict(id=L["id"], name=L["name"], line1=L["line1"], tax=L["tax"]) for L in LOCATIONS]
    data = json.dumps(dict(items=items, stores=stores)).replace("</", "<\\/")
    seg = "".join(f'<button type="button" data-store="{L["id"]}" data-loc-id="{L["id"]}" aria-pressed="false"><b>{L["name"]}</b><span>{L["line1"]}</span></button>' for L in LOCATIONS)
    chips = "".join(f'<a href="#o-{c["slug"]}">{c["name"]}</a>' for c in CATS)
    body = f'''{header("order")}<main>
<div class="demo" role="note"><b>Demo preview.</b> Orders aren't sent to the cafe yet and no card is charged.</div>
<div class="wrap ptitle"><p class="eyebrow">Pickup</p><h1>Order online</h1>
<div class="setup"><div><p class="field" style="margin-bottom:6px">Pick up from</p>{near_box()}<div class="seg" role="group" aria-label="Pickup location">{seg}</div></div>
<label class="field">Pickup time<select id="pickup"><option>ASAP (about 15 min)</option></select></label></div></div>
<nav class="chips" aria-label="Order sections"><div class="wrap">{chips}</div></nav>
<div class="wrap olayout"><div>{secs}</div>
<aside class="cart" id="cart" aria-label="Your order"><header><h2 id="c-title">Your order</h2><button class="x" type="button" aria-label="Close order">✕</button></header>
<div class="body" id="c-body"></div><div class="foot" id="c-foot"></div></aside></div></main>
<div class="scrim" id="scrim" hidden></div>
<button class="cartbar" id="cartbar" type="button" hidden><span class="ct" id="cb-count"></span><span>View order</span><span id="cb-total"></span></button>
<div class="sheet" id="sheet" hidden role="dialog" aria-modal="true" aria-labelledby="s-name"><div class="box" style="position:relative"><button class="close" type="button" aria-label="Close">✕</button><img src="" alt="">
<div class="in"><h3 id="s-name"></h3><p class="price" id="s-price"></p><p class="desc" id="s-desc"></p><div id="s-opts"></div>
<label class="field" style="margin-top:18px">Special instructions<textarea id="s-note" rows="2" placeholder="Optional"></textarea></label></div>
<div class="bar"><div class="step"><button type="button" id="s-minus" aria-label="Fewer">−</button><span id="s-qty">1</span><button type="button" id="s-plus" aria-label="More">+</button></div>
<button class="btn" type="button" id="s-add">Add to order</button></div></div></div>
<div id="toast" hidden role="status" class="toast" style="background:var(--ink);color:#fff;border-radius:999px;padding:10px 18px;font-size:.9rem;box-shadow:var(--shadow)"></div>
<script type="application/json" id="menu-data">{data}</script>
{footer()}'''
    return page("Order Online · Misree Chai", "Order Misree Chai online for pickup in Jersey City or Jackson Heights.", body, extra_js=ORDER_JS)

def build_visit():
    strip = "".join(f'<img src="{sm(n)}" alt="" loading="lazy" width="520" height="391">' for n in ["cafe-interior", "chai-cheers", "masala-chai", "triple-chocolate-crepe", "taro-milk-tea", "bun-maska"])
    L0 = LOCATIONS[0]
    tabs = "".join(f'<button type="button" role="tab" class="loc-tab" data-loc-id="{L["id"]}" aria-selected="{"true" if i == 0 else "false"}" data-loc="{L["id"]}" data-embed="{L["embed"]}" data-dir="{L["dir"]}" '
                   f'data-l1="{esc(L["line1"])}" data-l2="{esc(L["line2"])}" data-phone="{L["phone"]}" data-name="{L["name"]}"><b>{L["name"]}</b><span>{L["line1"]}</span></button>' for i, L in enumerate(LOCATIONS))
    body = f'''{header("visit")}<main>
<div class="wrap ptitle"><p class="eyebrow">Jersey City · Jackson Heights</p><h1>Visit us</h1><p class="muted">Pull up a chair for a glass of chai, or grab a kulfi milk tea and a crepe to go.</p>
{near_box()}<div class="loc-tabs" role="tablist" aria-label="Choose a location">{tabs}</div>
<div class="bigmap"><div class="map-fallback"><img src="{sm("cafe-interior")}" alt=""><span>The live Google Map loads here on the published site.</span></div>
<iframe id="loc-map" src="{L0["embed"]}" title="Google Map showing Misree Chai" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
<div class="mapbar"><div><p class="eyebrow" id="loc-name" style="margin-bottom:4px">Misree Chai · {L0["name"]}</p><h3 id="loc-l1">{L0["line1"]}, {L0["line2"]}</h3><p class="muted" id="loc-meta">Open daily · {L0["phone"]}</p></div>
<div class="acts"><a class="btn" id="loc-dir" href="{L0["dir"]}" target="_blank" rel="noopener">Directions</a><a class="btn line" id="loc-order" href="order.html?store={L0["id"]}">Order pickup</a></div></div></div>
<section class="pad"><div class="wrap"><div class="head"><h2>Inside Misree</h2><a href="{INSTA}" target="_blank" rel="noopener">@misreechai →</a></div><div class="strip">{strip}</div></div></section>
</main>{footer()}'''
    return page("Visit · Misree Chai", "Find Misree Chai in Jersey City and Jackson Heights: maps and directions.", body)


# Block-print wallpaper and ornaments, drawn as SVG so they stay crisp and tiny.
def buta(cx, cy, s, bg):
    g = f'<g transform="translate({cx} {cy}) scale({s})">'
    g += '<path d="M0 38 C-2 24 3 12 0 -4" fill="none" stroke="var(--l)" stroke-width="2.2" stroke-linecap="round"/>'
    g += '<path d="M-14 40 Q0 30 14 40" fill="none" stroke="var(--l)" stroke-width="2"/>'
    for d in (1, -1):
        g += f'<path d="M{d} 22 C{d*10} 12 {d*22} 14 {d*26} 6 C{d*16} 4 {d*6} 12 {d} 22Z" fill="var(--l)"/>'
        g += f'<path d="M{d} 22 C{d*10} 15 {d*18} 12 {d*24} 7" fill="none" stroke="{bg}" stroke-width=".9"/>'
        g += f'<path d="M0 8 C{d*8} 2 {d*12} -2 {d*16} -10 C{d*8} -9 {d*2} -2 0 8Z" fill="var(--l)" opacity=".75"/>'
    for a in (-64, -32, 0, 32, 64):
        g += f'<path transform="rotate({a} 0 -6)" d="M0 -6 C-6 -14 -5 -26 0 -32 C5 -26 6 -14 0 -6Z" fill="var(--f)" opacity="{1 if a == 0 else .82}"/>'
        g += f'<path transform="rotate({a} 0 -6)" d="M0 -9 L0 -27" stroke="{bg}" stroke-width=".8"/>'
    g += f'<circle cx="0" cy="-6" r="4.2" fill="var(--l)"/><circle cx="0" cy="-6" r="1.8" fill="{bg}"/>'
    g += "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="var(--f)"/>' for x, y in ((0, -38), (-10, -35), (10, -35)))
    return g + '</g>'

def star(cx, cy, color):
    g = f'<g transform="translate({cx} {cy})" fill="{color}">'
    g += "".join(f'<path transform="rotate({a})" d="M0 0 C-3 -3 -3 -8 0 -10 C3 -8 3 -3 0 0Z" opacity=".75"/>' for a in (0, 90, 180, 270))
    return g + '<circle r="1.6"/></g>'

def wallpaper(leaf, flower, bg, op):
    body = "".join(buta(x, y, .78, bg) for x, y in ((30, 50), (90, 135), (90, -35))) + "".join(star(x, y, leaf) for x, y in ((90, 50), (30, 135), (30, -35)))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="170" viewBox="0 0 120 170"><rect width="120" height="170" fill="{bg}"/>'
            f'<g opacity="{op}">{body.replace("var(--l)", leaf).replace("var(--f)", flower)}</g></svg>')

def ornament(color, flower):
    lotus = buta(70, 13, .32, "none").replace('var(--l)', color).replace('var(--f)', flower)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="140" height="26" viewBox="0 0 140 26">'
            f'<path d="M4 15H52M88 15H136" stroke="{color}" stroke-width="1.2"/><circle cx="56" cy="15" r="1.8" fill="{color}"/><circle cx="84" cy="15" r="1.8" fill="{color}"/>'
            f'<circle cx="4" cy="15" r="1.6" fill="{color}"/><circle cx="136" cy="15" r="1.6" fill="{color}"/>{lotus}</svg>')

def border_tile():
    gold = "#c9a55a"
    tiny = buta(30, 15.5, .26, "#2b1d14").replace('var(--l)', gold).replace('var(--f)', "#c46a52")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="60" height="30" viewBox="0 0 60 30"><rect width="60" height="30" fill="#2b1d14"/>'
            f'<path d="M0 3.5H60M0 26.5H60" stroke="{gold}" stroke-width="1"/><path d="M0 6H60M0 24H60" stroke="{gold}" stroke-width=".5" opacity=".6"/>'
            f'{tiny}<circle cx="0" cy="15" r="2" fill="{gold}"/><circle cx="60" cy="15" r="2" fill="{gold}"/></svg>')

def write_ornaments(out):
    d = os.path.join(out, "assets", "img"); os.makedirs(d, exist_ok=True)
    files = {"wallpaper.svg": wallpaper("#5f5820", "#9a4434", "#f5ecdc", .2),
             "wallpaper-dark.svg": wallpaper("#c9a55a", "#c46a52", "#2b1d14", .22),
             "orn.svg": ornament("#8a7a3a", "#9a4434"), "orn-light.svg": ornament("#e1c37d", "#e8a08a"), "border.svg": border_tile()}
    for n, svg in files.items():
        with open(os.path.join(d, n), "w") as fh:
            fh.write(svg)

os.makedirs(OUT, exist_ok=True)
write_ornaments(OUT)
for name, fn in [("index.html", build_index), ("menu.html", build_menu), ("order.html", build_order), ("visit.html", build_visit)]:
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(fn())
print("built", OUT)
