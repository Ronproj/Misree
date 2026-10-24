"""Misree Chai static site generator (minimal mobile-first edition).
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
/* Misree Chai: one small system. Warm white, near-black ink, olive accent from the logo.
   Type: 34/24/18/16/14. Radius: 16 cards, 12 controls. Spacing on an 4px grid. Mobile first. */
:root{
  --bg:#faf6ef; --surface:#ffffff; --soft:#f2ece2; --ink:#221a14; --muted:#6b6258; --line:#e9e1d4; --line-2:#d9cfc0;
  --accent:#5f5820; --night:#221a14;
  --hh:56px; --tab:62px; --safe-b:env(safe-area-inset-bottom,0px); --gut:20px;
  --font:"Jost",system-ui,-apple-system,"Segoe UI",sans-serif;
  --r:16px; --r-sm:12px;
  color-scheme:light;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%;scroll-padding-top:calc(var(--hh) + 64px)}
body{margin:0;background:var(--bg) url(assets/img/wallpaper.svg) repeat;background-size:120px 170px;color:var(--ink);font:400 16px/1.5 var(--font);-webkit-font-smoothing:antialiased;
  padding-bottom:calc(var(--tab) + var(--safe-b));-webkit-tap-highlight-color:transparent}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%;height:auto}
button{font:inherit;color:inherit}
h1,h2,h3,p{margin:0}
h1,h2,h3{font-weight:400;letter-spacing:-.01em;line-height:1.15;text-wrap:balance}
h1{font-size:34px}
h2{font-size:24px}
h3{font-size:18px;font-weight:500}
.muted{color:var(--muted)}
.small{font-size:14px}
.wrap{max-width:1180px;margin:0 auto;padding-left:max(var(--gut),env(safe-area-inset-left,0px));padding-right:max(var(--gut),env(safe-area-inset-right,0px))}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:6px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:48px;padding:0 20px;border:0;border-radius:var(--r-sm);
  background:var(--ink);color:#fff;font-size:15px;font-weight:500;white-space:nowrap;cursor:pointer;transition:transform .12s,opacity .12s}
.btn:active{transform:scale(.98)}
.btn.sec{background:var(--surface);color:var(--ink);box-shadow:inset 0 0 0 1px var(--line-2)}
.btn.block{width:100%}
.btn[disabled]{opacity:.4;cursor:not-allowed}
.sec-pad{padding-block:40px}
.shead{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:16px}
.shead a{font-size:15px;font-weight:500;color:var(--accent);padding:8px 0}
@media (min-width:900px){
  :root{--hh:68px;--tab:0px;--gut:32px}
  h1{font-size:48px} h2{font-size:32px}
  .sec-pad{padding-block:72px}
  .shead{margin-bottom:24px}
}

/* header */
.top{position:sticky;top:0;z-index:30;background:rgba(250,246,239,.92);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  border-bottom:1px solid var(--line);padding-top:env(safe-area-inset-top,0px)}
.top .wrap{display:flex;align-items:center;gap:24px;height:var(--hh)}
.brand{display:flex;align-items:center;gap:10px;font-size:18px;font-weight:500}
.brand img{width:32px;height:32px;border-radius:50%;border:1px solid var(--line)}
.nav{display:none;gap:4px;margin-left:auto}
.nav a{padding:8px 12px;border-radius:10px;font-size:15px;color:var(--muted)}
.nav a:hover{color:var(--ink)}
.nav a[aria-current]{color:var(--ink);background:var(--soft)}
.top .btn{display:none;height:40px;font-size:14px}
@media (min-width:900px){.nav{display:flex}.top .btn{display:inline-flex}}
.top.over{position:fixed;left:0;right:0;transition:background .25s,border-color .25s,color .25s}
.top.over:not(.solid){background:transparent;border-color:transparent;backdrop-filter:none;-webkit-backdrop-filter:none;color:#fff}
.top.over:not(.solid) .brand img{border-color:transparent}
.top.over:not(.solid) .nav a{color:rgba(255,255,255,.85)}
.top.over:not(.solid) .nav a[aria-current]{background:rgba(255,255,255,.15);color:#fff}
.top.over:not(.solid) .btn{background:#fff;color:var(--ink)}

/* bottom tab bar on phones */
.tabbar{position:fixed;left:0;right:0;bottom:0;z-index:40;display:grid;grid-template-columns:repeat(5,1fr);background:rgba(255,255,255,.96);
  backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-top:1px solid var(--line);padding:0 env(safe-area-inset-right,0px) var(--safe-b) env(safe-area-inset-left,0px)}
.tabbar a{height:var(--tab);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;font-size:11px;font-weight:500;color:#8c8379}
.tabbar svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.tabbar a[aria-current]{color:var(--ink)}
.tabbar a[aria-current] svg{stroke-width:2.1}
@media (min-width:900px){.tabbar{display:none}}

/* home hero: one full-screen photo */
.hero{position:relative;height:calc(100svh - var(--tab) - var(--safe-b));min-height:520px;max-height:980px;display:flex;align-items:flex-end;
  color:#fff;background:var(--night);overflow:hidden;isolation:isolate}
.hero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:36% center;z-index:-2}
.hero::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,rgba(20,12,6,.5) 0%,rgba(20,12,6,0) 24%,rgba(20,12,6,.2) 50%,rgba(20,12,6,.86) 100%)}
.hero .wrap{width:100%;padding-bottom:32px}
.kicker{font-size:14px;color:rgba(255,255,255,.8);margin-bottom:8px}
.hero h1{font-size:52px;font-weight:300;line-height:1}
.hero .lede{color:rgba(255,255,255,.88);max-width:32ch;margin:12px 0 24px}
.hero .ctas{display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:400px}
.hero .btn{background:#fff;color:var(--ink)}
.hero .btn.ghost{background:rgba(255,255,255,.16);color:#fff;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
@media (min-width:900px){.hero .wrap{padding-bottom:80px}.hero h1{font-size:96px}.hero .lede{font-size:18px}}

/* swipeable rows on phones, grids on desktop */
.rail{display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-padding-inline:var(--gut);
  margin-inline:calc(var(--gut) * -1);padding:0 var(--gut) 4px;scrollbar-width:none}
.rail::-webkit-scrollbar{display:none}
.rail>*{flex:none;scroll-snap-align:start}
.cat{width:128px}
.cat img,.pick img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:var(--r);background:var(--soft)}
.cat b,.pick b{display:block;margin-top:8px;font-size:15px;font-weight:500;line-height:1.3}
.cat span,.pick span{font-size:14px;color:var(--muted)}
.pick{width:160px}
.pick .ph{position:relative}
.pick i{position:absolute;right:8px;bottom:8px;width:32px;height:32px;border-radius:50%;background:#fff;display:grid;place-items:center;
  font-style:normal;font-size:20px;line-height:1;box-shadow:0 2px 8px rgba(0,0,0,.15)}
.strip img{width:220px;aspect-ratio:4/5;object-fit:cover;border-radius:var(--r)}
@media (min-width:900px){
  .rail{display:grid;overflow:visible;margin:0;padding:0;gap:20px}
  .rail.cats{grid-template-columns:repeat(6,1fr)}
  .rail.picks{grid-template-columns:repeat(4,1fr)}
  .rail.strip{grid-template-columns:repeat(6,1fr)}
  .cat,.pick{width:auto}
  .strip img{width:100%}
}

/* home sections */
.promo{background:var(--night) url(assets/img/wallpaper-dark.svg);background-size:120px 170px;color:#fff;border-radius:var(--r);padding:28px 24px}
.promo p{color:rgba(255,255,255,.75);margin:8px 0 20px}
.promo .btn{background:#fff;color:var(--ink)}
@media (min-width:900px){.promo{display:flex;align-items:center;justify-content:space-between;gap:32px;padding:44px 48px}.promo p{margin-bottom:0}}
.story{display:grid;gap:20px}
.story img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:var(--r)}
.story p{color:var(--muted);margin-top:12px;max-width:52ch}
@media (min-width:900px){.story{grid-template-columns:1fr 1fr;gap:56px;align-items:center}.story img{aspect-ratio:4/3}}
.app{background:var(--soft);border-radius:var(--r);padding:28px 24px;display:grid;gap:20px}
.app p{color:var(--muted);margin-top:8px;max-width:44ch}
.stores{display:flex;gap:10px;flex-wrap:wrap}
.store{display:inline-flex;flex-direction:column;justify-content:center;height:52px;padding:0 18px;border-radius:var(--r-sm);background:var(--ink);color:#fff;line-height:1.15}
.store small{font-size:11px;opacity:.75}
.store b{font-size:16px;font-weight:500}
.store[aria-disabled="true"]{opacity:.4}
@media (min-width:900px){.app{grid-template-columns:1fr auto;align-items:center;padding:44px 48px}}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r)}
.locs{display:grid;gap:12px}
.loc{padding:20px}
.loc p{font-size:15px;color:var(--muted);margin-top:2px}
.acts{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px}
@media (min-width:760px){.locs{grid-template-columns:1fr 1fr;gap:20px}}

footer{background:var(--night) url(assets/img/wallpaper-dark.svg);background-size:120px 170px;color:rgba(255,248,236,.66);font-size:14px;padding-block:32px 40px}
footer .wrap{display:grid;gap:16px}
footer .brand{color:#fff}
footer nav{display:flex;flex-wrap:wrap;gap:2px 20px}
footer nav a{color:#fff8ec;padding:6px 0}

/* page heads and sticky section tabs */
.phead{padding-block:28px 22px;background:var(--night) url(assets/img/wallpaper-dark.svg);background-size:120px 170px;color:#fff}
.phead p{margin-top:6px;color:rgba(255,248,236,.72)}
@media (min-width:900px){.phead{padding-block:48px 24px}}
.chips{position:sticky;top:calc(var(--hh) + env(safe-area-inset-top,0px));z-index:20;background:rgba(250,246,239,.95);
  backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
.chips .wrap{display:flex;gap:8px;overflow-x:auto;padding-block:10px;scrollbar-width:none}
.chips .wrap::-webkit-scrollbar{display:none}
.chips a{flex:none;height:36px;display:inline-flex;align-items:center;padding:0 14px;border-radius:999px;background:var(--soft);color:var(--muted);font-size:14px;font-weight:500}
.chips a[aria-current]{background:var(--ink);color:#fff}

/* item rows: text left, photo right (menu and order) */
.rows{list-style:none;margin:0;padding:0}
.row{display:grid;grid-template-columns:minmax(0,1fr) 84px;gap:16px;align-items:center;width:100%;padding:14px 0;border:0;border-bottom:1px solid var(--line);
  background:none;text-align:left;cursor:pointer}
.row .n{display:block;font-size:16px;font-weight:500;line-height:1.3}
.row small{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:2px;font-size:14px;line-height:1.4;color:var(--muted)}
.row .p{display:block;margin-top:6px;font-size:15px}
.row .ph{position:relative}
.row img{width:84px;height:84px;object-fit:cover;border-radius:var(--r-sm);background:var(--soft)}
.row .add{position:absolute;right:-6px;bottom:-6px;width:30px;height:30px;border-radius:50%;background:var(--surface);display:grid;place-items:center;
  font-size:19px;line-height:1;box-shadow:0 1px 6px rgba(0,0,0,.18)}
.row .qtyb{position:absolute;left:-6px;top:-6px;min-width:22px;height:22px;padding:0 6px;border-radius:999px;background:var(--ink);color:#fff;
  font-size:12px;font-weight:600;display:grid;place-items:center}

/* menu page */
.mgroup{scroll-margin-top:calc(var(--hh) + 60px);overflow:hidden}
.mban{position:relative;margin:calc(var(--pp) * -1) calc(var(--pp) * -1) 8px;color:#fff}
.mban img{display:block;width:100%;aspect-ratio:16/8;object-fit:cover}
.mban::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(20,14,10,0) 35%,rgba(20,14,10,.78))}
.mban div{position:absolute;left:var(--pp);right:var(--pp);bottom:16px;z-index:1;display:flex;align-items:baseline;justify-content:space-between;gap:12px}
.mban h2{font-size:32px;font-weight:400;color:#fff}
.mban span{font-size:14px;color:rgba(255,248,236,.8)}
.msub{display:flex;align-items:center;gap:14px;margin:26px 0 6px;font-size:13px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);scroll-margin-top:calc(var(--hh) + 60px)}
.msub::before,.msub::after{content:"";flex:1;height:1px;background:var(--line-2)}
.mlist{list-style:none;margin:0;padding:0}
.mi{display:block;width:100%;padding:14px 0;border:0;border-bottom:1px dashed var(--line-2);background:none;text-align:left;font:inherit;color:inherit;cursor:pointer}
.mlist li:last-child .mi{border-bottom:0}
.mi .mt{display:flex;align-items:baseline;gap:8px}
.mi .n{font-size:17px;font-weight:500}
.mi .dots{flex:1;min-width:16px;border-bottom:2px dotted var(--line-2);transform:translateY(-4px)}
.mi .p{font-size:16px;font-weight:500;font-variant-numeric:tabular-nums}
.mi small{display:block;margin-top:3px;font-size:14px;line-height:1.45;color:var(--muted);max-width:52ch}
.mi:hover .n{color:var(--accent)}
.note{font-size:14px;color:var(--muted);text-align:center;margin:32px auto 0;max-width:46ch}
.endcta{display:flex;justify-content:center;margin:20px 0 48px}
@media (min-width:900px){
  .mban img{aspect-ratio:16/4.5}
  .mban div{bottom:24px}
  .mban h2{font-size:44px}
  .mlist{display:grid;grid-template-columns:1fr 1fr;column-gap:56px}
  .mlist li:nth-last-child(2):nth-child(odd) .mi{border-bottom:0}
}

/* order page */
.obar{padding:24px 0 20px;background:var(--night) url(assets/img/wallpaper-dark.svg);background-size:120px 170px;color:#fff}
.obar .demo{font-size:13px;color:rgba(255,248,236,.72);margin-top:4px}
.obar .psum{border-color:transparent;color:var(--ink)}
.psum{display:flex;align-items:center;gap:12px;width:100%;margin-top:16px;padding:12px 14px;background:var(--surface);border:1px solid var(--line);
  border-radius:var(--r);text-align:left;cursor:pointer}
.psum svg{flex:none;width:22px;height:22px;fill:none;stroke:var(--ink);stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.psum b{display:block;font-weight:500}
.psum>span{min-width:0;flex:1}
.psum span span{display:block;font-size:14px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.psum em{margin-left:auto;font-style:normal;font-size:14px;font-weight:500;color:var(--accent)}
.lbl{display:block;font-size:13px;color:var(--muted);margin-bottom:8px}
.seg{display:grid;gap:8px}
.seg button{display:block;width:100%;padding:14px 16px;border:1px solid var(--line);border-radius:var(--r-sm);background:var(--surface);text-align:left;cursor:pointer}
.seg button b{display:block;font-weight:500}
.seg button span{font-size:14px;color:var(--muted)}
.seg button[aria-pressed="true"]{border-color:var(--ink);box-shadow:inset 0 0 0 1px var(--ink)}
.seg button.is-near b::after{content:"Closest";margin-left:8px;font-size:12px;font-weight:500;color:var(--accent)}
select,input,textarea{width:100%;min-height:48px;padding:12px 14px;font:inherit;font-size:16px;color:var(--ink);background:var(--surface);border:1px solid var(--line-2);border-radius:var(--r-sm)}
select:focus,input:focus,textarea:focus{outline:none;border-color:var(--ink)}
.field{display:flex;flex-direction:column;gap:6px;font-size:14px;color:var(--muted)}
.ocontrols{position:fixed;left:0;right:0;bottom:0;z-index:60;display:grid;gap:18px;background:var(--surface);border-radius:20px 20px 0 0;
  padding:20px var(--gut) calc(20px + var(--safe-b));transform:translateY(105%);visibility:hidden;transition:transform .26s cubic-bezier(.2,.8,.2,1),visibility .26s}
.ocontrols.open{transform:none;visibility:visible}
.olayout{display:grid;gap:24px;padding-bottom:32px}
.oside{display:none}
.osec{padding-top:24px;scroll-margin-top:calc(var(--hh) + 60px)}
.osec h2{font-size:20px;font-weight:500;margin-bottom:2px}
@media (min-width:900px){
  .obar{background:var(--night) url(assets/img/wallpaper-dark.svg);background-size:120px 170px;color:#fff;padding:32px 0}
  .obar .wrap{display:flex;align-items:flex-end;justify-content:space-between;gap:32px}
  .obar .demo{color:rgba(255,248,236,.66)}
  .psum,.ocontrols .phd,#pdone{display:none}
  .ocontrols{position:static;transform:none;visibility:visible;transition:none;background:none;padding:0;border-radius:0;grid-template-columns:400px 200px;gap:12px;align-items:end}
  .ocontrols .lbl{color:rgba(255,248,236,.66)}
  .ocontrols .seg{grid-template-columns:1fr 1fr;gap:4px;padding:4px;background:rgba(255,255,255,.1);border-radius:var(--r-sm)}
  .ocontrols .seg button{border:0;background:none;color:#fff;padding:8px 12px;border-radius:9px;box-shadow:none}
  .ocontrols .seg button span{color:rgba(255,248,236,.6)}
  .ocontrols .seg button[aria-pressed="true"]{background:#fff;color:var(--ink)}
  .ocontrols .seg button[aria-pressed="true"] span{color:var(--muted)}
  .ocontrols select{height:58px;border:0}
  .osec h2{font-size:24px;font-weight:400;margin-bottom:14px}
  .opage .wrap{max-width:1360px}
  .obar{padding:24px 0}
  .ogrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
  .ogrid .row{grid-template-columns:minmax(0,1fr) 104px;gap:14px;padding:14px;border:1px solid var(--line);border-radius:var(--r);background:var(--surface);transition:border-color .15s,box-shadow .15s}
  .ogrid .row:hover{border-color:var(--line-2);box-shadow:0 4px 14px rgba(34,26,20,.08)}
  .ogrid .row img{width:104px;height:104px}
  .ogrid .row .txt{align-self:stretch;display:flex;flex-direction:column}
  .ogrid .row .p{margin-top:auto;padding-top:6px}
}
@media (min-width:1000px){.olayout{grid-template-columns:minmax(0,1fr) 340px;gap:24px}}
@media (min-width:900px) and (max-width:1199px){.opage .cart{top:calc(var(--hh) + 74px);max-height:calc(100vh - var(--hh) - 90px)}}
@media (min-width:1200px){
  .opage .chips{display:none}
  .olayout{grid-template-columns:190px minmax(0,1fr) 340px}
  .oside{display:flex;flex-direction:column;position:sticky;top:calc(var(--hh) + 16px);align-self:start}
  .oside a{padding:9px 0 9px 14px;border-left:2px solid var(--line);color:var(--muted);font-weight:500}
  .oside a[aria-current]{color:var(--ink);border-color:var(--ink)}
}

/* cart: sidebar on desktop, bottom sheet on phones */
.cart{background:var(--surface);display:flex;flex-direction:column;overflow:hidden}
.cart header{display:flex;justify-content:space-between;align-items:center;padding:16px 20px;border-bottom:1px solid var(--line)}
.cart header h2{font-size:20px;font-weight:500}
.x{width:36px;height:36px;border:0;border-radius:50%;background:var(--soft);font-size:15px;cursor:pointer}
.cart .body{flex:1;overflow:auto;padding:0 20px}
.cart .foot{padding:16px 20px 20px;border-top:1px solid var(--line)}
.cart .foot:empty{display:none}
.cline{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 12px;padding:14px 0;border-bottom:1px solid var(--line)}
.cline b{font-weight:500}
.cline small{grid-column:1;font-size:13px;color:var(--muted)}
.step{display:inline-flex;align-items:center;width:max-content;margin-top:8px;background:var(--soft);border-radius:999px}
.step button{width:36px;height:34px;border:0;background:none;font-size:17px;cursor:pointer}
.step span{min-width:18px;text-align:center;font-size:15px}
.sum{display:grid;grid-template-columns:1fr auto;gap:4px;margin-bottom:16px;font-size:15px;color:var(--muted)}
.sum b{color:var(--ink);font-weight:500;font-size:17px;margin-top:4px}
.empty{padding:32px 0;text-align:center;color:var(--muted)}
.form{display:grid;gap:14px;padding-bottom:8px}
.paybox{display:grid;gap:8px;padding:14px;border:1px dashed var(--line-2);border-radius:var(--r-sm);font-size:14px;color:var(--muted)}
.paybox .rowx{display:grid;grid-template-columns:1fr 96px;gap:8px}
.done{text-align:center;padding:20px 0 8px}
.done .tick{width:56px;height:56px;margin:0 auto 14px;border-radius:50%;background:var(--accent);color:#fff;display:grid;place-items:center;font-size:24px}
.done h3{font-size:22px;font-weight:400;margin-bottom:6px}
.back{padding:12px 0;border:0;background:none;color:var(--accent);font-weight:500;cursor:pointer}
@media (min-width:1000px){
  .cart{position:sticky;top:calc(var(--hh) + 16px);margin-top:16px;align-self:start;max-height:calc(100vh - var(--hh) - 32px);border:1px solid var(--line);border-radius:var(--r);box-shadow:0 1px 3px rgba(34,26,20,.06)}
  .cart .x{display:none}
  .cartbar{display:none!important}
}
@media (max-width:999px){
  .cart{position:fixed;left:0;right:0;bottom:0;z-index:60;max-height:88vh;border-radius:20px 20px 0 0;padding-bottom:var(--safe-b);
    transform:translateY(105%);visibility:hidden;transition:transform .26s cubic-bezier(.2,.8,.2,1),visibility .26s}
  .cart.open{transform:none;visibility:visible}
}
.cartbar{position:fixed;left:var(--gut);right:var(--gut);bottom:calc(var(--tab) + var(--safe-b) + 10px);z-index:35;height:56px;display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:0 18px;border:0;border-radius:14px;background:var(--ink);color:#fff;font-weight:500;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.22)}
.cartbar .ct{padding:2px 10px;border-radius:999px;background:rgba(255,255,255,.16);font-size:14px}
.has-cartbar{padding-bottom:calc(var(--tab) + var(--safe-b) + 80px)}
.scrim{position:fixed;inset:0;z-index:55;background:rgba(20,14,8,.42)}
.toast{position:fixed;left:50%;bottom:calc(var(--tab) + var(--safe-b) + 78px);transform:translateX(-50%);z-index:80;white-space:nowrap;
  padding:10px 16px;border-radius:999px;background:var(--ink);color:#fff;font-size:14px;box-shadow:0 6px 20px rgba(0,0,0,.2)}
@media (min-width:1000px){.toast{bottom:28px}}

/* bottom sheets: item details and menu quick view */
.sheet{position:fixed;inset:0;z-index:70;display:flex;align-items:flex-end;justify-content:center;background:rgba(20,14,8,.45)}
.sheet .box{position:relative;display:flex;flex-direction:column;width:100%;max-width:520px;max-height:90vh;overflow:auto;background:var(--surface);
  border-radius:20px 20px 0 0;padding-bottom:var(--safe-b);animation:up .22s ease-out}
.sheet .box>img{flex:none;width:100%;aspect-ratio:16/10;object-fit:cover}
.sheet .in{padding:20px var(--gut) 8px}
.sheet h3{font-size:24px;font-weight:400}
.sheet .price{margin-top:4px;font-size:17px;font-weight:500}
.sheet .desc{margin-top:8px;color:var(--muted)}
.sheet fieldset{margin:20px 0 0;padding:0;border:0}
.sheet legend{margin-bottom:10px;font-size:15px;font-weight:500}
.opts{display:flex;flex-wrap:wrap;gap:8px}
.opts label{position:relative}
.opts input{position:absolute;opacity:0;width:1px;height:1px;min-height:0}
.opts span{display:block;padding:9px 16px;border:1px solid var(--line-2);border-radius:999px;font-size:15px;cursor:pointer}
.opts input:checked+span{background:var(--ink);border-color:var(--ink);color:#fff}
.opts input:focus-visible+span{outline:2px solid var(--accent);outline-offset:2px}
.sheet .bar{position:sticky;bottom:0;display:flex;align-items:center;gap:10px;margin-top:auto;padding:14px var(--gut) 16px;background:var(--surface);border-top:1px solid var(--line)}
.sheet .bar .step{margin:0}
.sheet .bar .btn{flex:1}
.sheet .close{position:absolute;top:12px;right:12px;z-index:1;width:36px;height:36px;border:0;border-radius:50%;background:rgba(255,255,255,.94);font-size:15px;cursor:pointer;box-shadow:0 1px 6px rgba(0,0,0,.15)}
@media (min-width:600px){.sheet{align-items:center;padding:24px}.sheet .box{border-radius:20px;max-height:88vh}}
@keyframes up{from{transform:translateY(32px);opacity:.6}}

/* visit page */
.ltabs{display:grid;grid-template-columns:1fr 1fr;gap:4px;padding:4px;margin:16px 0 12px;background:#ece3d3;border-radius:var(--r-sm)}
.loc-tab{height:44px;border:0;border-radius:9px;background:none;font-weight:500;color:var(--muted);cursor:pointer}
.loc-tab[aria-selected="true"]{background:var(--surface);color:var(--ink);box-shadow:0 1px 3px rgba(0,0,0,.08)}
.bigmap{position:relative;height:320px;overflow:hidden;border-radius:var(--r);background:var(--soft)}
.bigmap iframe,.bigmap .map-fallback{position:absolute;inset:0;width:100%;height:100%;border:0}
.bigmap .map-fallback img{width:100%;height:100%;object-fit:cover;opacity:.35}
.bigmap .map-fallback span{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);max-width:80%;padding:10px 14px;border-radius:var(--r-sm);background:var(--surface);font-size:14px;text-align:center}
.mapinfo{margin-top:12px;padding:20px}
.mapinfo p{font-size:15px;color:var(--muted);margin-top:2px}
@media (min-width:900px){
  .ltabs{max-width:420px}
  .bigmap{height:520px}
  .mapinfo{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:24px 28px}
  .mapinfo .acts{margin-top:0;display:flex}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
/* white reading panels over the wallpaper */
:root{--pp:16px}
@media (min-width:900px){:root{--pp:28px}}
.panel,.mgroup,.osec{background:#fff;border-radius:var(--r);padding:var(--pp);box-shadow:0 1px 3px rgba(34,26,20,.06)}
.mgroup,.osec{margin-top:16px}
.rows>li:last-child .row{border-bottom:0}
@media (max-width:899px){.ogrid>.row:last-child{border-bottom:0;padding-bottom:0}}
.panel .rail{margin-inline:calc(var(--pp) * -1);padding-inline:var(--pp);scroll-padding-inline:var(--pp)}
@media (min-width:900px){.panel .rail{margin-inline:0;padding-inline:0}}
.panel .card,.mgroup .card{box-shadow:none}
.story.panel{gap:16px}
.app{background:#fff}
.mapinfo{background:#fff}
.ltabs{background:#fff}
.ltabs .loc-tab[aria-selected="true"]{background:var(--ink);color:#fff}
@media (min-width:900px){.oside{background:#fff;border-radius:var(--r);padding:16px;margin-top:16px}}

/* rewards page */
.rwrap{display:grid;gap:16px}
.rhero{display:grid;gap:18px}
.rhero img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:var(--r-sm)}
.rhero p{color:var(--muted);margin:8px 0 18px;max-width:46ch}
.steps{list-style:none;margin:16px 0 0;padding:0;display:grid;gap:18px}
.steps li{display:grid;grid-template-columns:40px 1fr;gap:14px;align-items:start}
.steps .num{width:40px;height:40px;border-radius:50%;background:var(--ink);color:#fff;display:grid;place-items:center;font-weight:500}
.steps h3{font-size:17px;font-weight:500}
.steps p{color:var(--muted);font-size:15px;margin-top:2px}
@media (min-width:900px){.rhero{grid-template-columns:1.1fr 1fr;align-items:center;gap:36px}.steps{grid-template-columns:repeat(3,1fr);gap:28px}}

"""

JS = r"""
const over=document.querySelector('.top.over');
if(over){const f=()=>over.classList.toggle('solid',scrollY>40);addEventListener('scroll',f,{passive:true});f()}
// menu + order chips scrollspy
const chips=document.querySelectorAll('.chips a, .oside a');
if(chips.length){
  const spy=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)return;
    chips.forEach(a=>{const on=a.getAttribute('href').slice(1)===e.target.id;a.toggleAttribute('aria-current',on);if(on)a.setAttribute('aria-current','true');
      const w=a.parentElement;if(on&&w.scrollWidth>w.clientWidth)w.scrollTo({left:a.offsetLeft-w.clientWidth/2+a.clientWidth/2,behavior:'smooth'})})}),{rootMargin:'-18% 0px -72% 0px'});
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
const want=new URLSearchParams(location.search).get('store');if(D.stores.some(s=>s.id===want))state.store=want;
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
// pickup details: a summary row that opens a bottom sheet on phones
const pick=$('#pick'),pickOpen=()=>pick.classList.contains('open');
const openPick=()=>{pick.classList.add('open');scrim.hidden=false;document.body.style.overflow='hidden';pick.querySelector('[aria-pressed=true]')?.focus()};
const closePick=()=>{pick.classList.remove('open');if(!cartOpen()){scrim.hidden=true;document.body.style.overflow=''}if(pick.dataset.o){delete pick.dataset.o;$('#psum').focus()}};
$('#psum').addEventListener('click',()=>{pick.dataset.o=1;openPick()});$('#pdone').addEventListener('click',closePick);
function syncPick(){const s=store();$('#ps-store').textContent='Pickup at '+s.name;$('#ps-meta').textContent=s.line1+' · '+(sel.selectedIndex?sel.value:'ASAP (~15 min)')}
sel.addEventListener('change',syncPick);
bar.addEventListener('click',openCart);scrim.addEventListener('click',()=>pickOpen()?closePick():closeCart());cart.querySelector('.x').addEventListener('click',closeCart);
addEventListener('keydown',e=>{if(e.key!=='Escape')return;if(!sheet.hidden)closeItem();else if(pickOpen())closePick();else if(cartOpen())closeCart()});
const totals=()=>{const sub=state.cart.reduce((s,l)=>s+ITEMS.get(l.id).price*l.qty,0);const tax=Math.round(sub*store().tax*100)/100;return{sub,tax,total:sub+tax,count:state.cart.reduce((s,l)=>s+l.qty,0)}};
function render(){
  const t=totals(),body=$('#c-body'),foot=$('#c-foot'),s=store();syncPick();
  document.querySelectorAll('[data-add]').forEach(b=>{const n=state.cart.filter(l=>l.id===b.dataset.add).reduce((a,l)=>a+l.qty,0);const q=b.querySelector('.qtyb');q.hidden=!n;q.textContent=n});
  bar.hidden=!t.count||state.view==='done';document.body.classList.toggle('has-cartbar',!bar.hidden);
  $('#cb-count').textContent=t.count+(t.count===1?' item':' items');$('#cb-total').textContent=money(t.total);
  $('#c-title').textContent=state.view==='checkout'?'Checkout':state.view==='done'?'Order placed':'Your order';
  if(state.view==='done'){body.innerHTML=`<div class="done"><div class="tick" aria-hidden="true">✓</div><h3>Thanks, ${esc(state.name)}!</h3>
    <p class="muted">Order #${state.no} for pickup at Misree Chai ${s.name}, ${s.line1}. Ready ${esc(state.time)}.</p>
    <p class="muted small" style="margin-top:12px">This is a demo, so no order was sent and no card was charged.</p></div>`;
    foot.innerHTML='<button class="btn block" type="button" id="c-new">Start a new order</button>';
    $('#c-new').onclick=()=>{state.cart=[];state.view='cart';render();if(cartOpen())closeCart()};return}
  if(!state.cart.length){body.innerHTML='<p class="empty">Your bag is empty.<br>Tap any item to add it.</p>';foot.innerHTML='';state.view='cart';return}
  const sum=`<div class="sum"><span>Subtotal</span><span>${money(t.sub)}</span><span>Est. tax</span><span>${money(t.tax)}</span><b>Total</b><b>${money(t.total)}</b></div>`;
  if(state.view==='checkout'){
    body.innerHTML=`<button class="back" type="button" id="c-back">← Back to order</button>
    <p class="muted small" style="margin-bottom:14px">Pickup at <b style="color:var(--ink);font-weight:500">${s.name}</b>, ${s.line1} · ${esc(sel.value)}</p>
    <form class="form" id="c-form" novalidate><label class="field">Name<input name="name" autocomplete="given-name" required placeholder="Your name"></label>
    <label class="field">Phone, for a text when it's ready<input name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="(555) 555-0123"></label>
    <div class="paybox">Payment (demo, nothing is charged)<input aria-label="Card number" inputmode="numeric" placeholder="Card number" style="margin-top:8px"><div class="rowx"><input aria-label="Expiry" placeholder="MM / YY" inputmode="numeric"><input aria-label="CVC" placeholder="CVC" inputmode="numeric"></div></div></form>`;
    foot.innerHTML=sum+`<button class="btn block" type="submit" form="c-form">Place order · ${money(t.total)}</button>`;
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
// preselect the closest cafe, unless the link already chose one
const rad=x=>x*Math.PI/180,dist=(a,b,c,d)=>Math.sin(rad(c-a)/2)**2+Math.cos(rad(a))*Math.cos(rad(c))*Math.sin(rad(d-b)/2)**2;
if(!want&&navigator.geolocation)navigator.geolocation.getCurrentPosition(p=>{const {latitude:a,longitude:b}=p.coords;
  const n=[...D.stores].sort((x,y)=>dist(a,b,x.lat,x.lng)-dist(a,b,y.lat,y.lng))[0];
  segs.forEach(x=>x.classList.toggle('is-near',x.dataset.store===n.id));setStore(n.id)},()=>{},{timeout:10000,maximumAge:600000});
"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600&display=swap">'

def page(title, desc, body, is_index=False, extra_js=""):
    head = (f'<title>{title}</title><meta name="claude:viewport-fit-sides" content="cover"><meta name="theme-color" content="#faf6ef">'
            f'<meta name="description" content="{esc(desc)}"><meta property="og:image" content="{img("chai-pour")}"><link rel="icon" href="assets/img/logo.png">{FONTS}<style>{CSS}</style>')
    tail = f'<script>{JS}{extra_js}</script>'
    if ARTIFACT and is_index:
        return head + body + tail
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'{head}</head><body>{body}{tail}</body></html>')

ICONS = {
    "home": '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
    "menu": '<path d="M6 3.5h12a1 1 0 0 1 1 1v15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-15a1 1 0 0 1 1-1z"/><path d="M9 8.5h6M9 12h6M9 15.5h3.5"/>',
    "order": '<path d="M5.5 8h13l-1 12.5h-11z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/>',
    "rewards": '<path d="m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"/>',
    "visit": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
}
PIN = '<svg viewBox="0 0 24 24" aria-hidden="true">' + ICONS["visit"] + '</svg>'
NAV = [("home", "Home", "index.html"), ("menu", "Menu", "menu.html"), ("order", "Order", "order.html"),
       ("rewards", "Rewards", "rewards.html"), ("visit", "Visit", "visit.html")]

def header(current="home", over=False):
    cur = lambda k: ' aria-current="page"' if k == current else ""
    links = "".join(f'<a href="{h}"{cur(k)}>{"Join our Rewards Program" if k == "rewards" else t}</a>' for k, t, h in NAV if k != "order")
    tabs = "".join(f'<a href="{h}"{cur(k)}><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[k]}</svg>{t}</a>' for k, t, h in NAV)
    return (f'<header class="top{" over" if over else ""}"><div class="wrap"><a class="brand" href="index.html"><img src="assets/img/logo.png" alt="" width="32" height="32">Misree Chai</a>'
            f'<nav class="nav" aria-label="Main">{links}</nav><a class="btn" href="order.html"{cur("order")}>Order Online</a></div></header>'
            f'<nav class="tabbar" aria-label="Main">{tabs}</nav>')

def footer():
    return (f'<footer><div class="wrap"><a class="brand" href="index.html"><img src="assets/img/logo.png" alt="" width="32" height="32" loading="lazy">Misree Chai</a>'
            f'<nav aria-label="More"><a href="menu.html">Menu</a><a href="order.html">Order pickup</a><a href="rewards.html">Rewards</a><a href="visit.html">Visit</a>'
            f'<a href="{INSTA}" target="_blank" rel="noopener">Instagram</a><a href="{DOORDASH}" target="_blank" rel="noopener">DoorDash</a><a href="{UBER}" target="_blank" rel="noopener">Uber Eats</a></nav>'
            f'<p>Jersey City &amp; Jackson Heights. Prices are from the cafe\'s online ordering menu and may change. Photos are styled representations.</p></div></footer>')

def loc_cards():
    def card(L):
        meta = f'Open daily · {L["phone"]}' if L["phone"] else "Open daily"
        return (f'<div class="card loc"><h3>{L["name"]}</h3><p>{L["line1"]}, {L["line2"]}</p><p>{meta}</p>'
                f'<div class="acts"><a class="btn sec" href="{L["dir"]}" target="_blank" rel="noopener">Directions</a><a class="btn" href="order.html?store={L["id"]}">Order</a></div></div>')
    return f'<div class="locs">{"".join(card(L) for L in LOCATIONS)}</div>'

def build_index():
    cats = "".join(f'<a class="cat" href="menu.html#{c["slug"]}"><img src="{sm(c["items"][0][2])}" alt="" loading="lazy" width="520" height="520"><b>{c["name"]}</b><span>{len(c["items"])} items</span></a>' for c in CATS)
    picks_src = [("kulfi", 0), ("chai", 0), ("crepes", 0), ("bowls", 0)]
    picks = "".join((lambda n, p, im, d: f'<a class="pick" href="order.html"><span class="ph"><img src="{sm(im)}" alt="" loading="lazy" width="520" height="520"><i aria-hidden="true">+</i></span><b>{n}</b><span>${p}</span></a>')(*BYSLUG[s]["items"][i]) for s, i in picks_src)
    body = f'''{header("home", over=True)}
<main>
<section class="hero"><img src="{img("chai-pour")}" alt="Chai being poured into small glasses" width="1400" height="1054" fetchpriority="high">
<div class="wrap"><p class="kicker">Jersey City · Jackson Heights</p><h1>Misree Chai</h1>
<p class="lede">Masala chai, kulfi milk tea, crepes and acai bowls, made fresh every day.</p>
<div class="ctas"><a class="btn" href="order.html">Order pickup</a><a class="btn ghost" href="menu.html">View menu</a></div></div></section>
<section class="sec-pad"><div class="wrap"><div class="panel"><div class="shead"><h2>Menu</h2><a href="menu.html">See all</a></div><div class="rail cats">{cats}</div></div></div></section>
<section class="sec-pad" style="padding-top:0"><div class="wrap"><div class="panel"><div class="shead"><h2>Start here</h2><a href="order.html">Order</a></div><div class="rail picks">{picks}</div></div></div></section>
<section class="sec-pad" style="padding-top:0"><div class="wrap"><div class="promo"><div><h2>Skip the line</h2>
<p>Order ahead and pick up at Jersey City or Jackson Heights.</p></div><a class="btn" href="order.html">Start an order</a></div></div></section>
<section class="sec-pad" style="padding-top:0"><div class="wrap"><div class="story panel"><img src="{img("misri")}" alt="Misri rock sugar beside a glass of chai" loading="lazy" width="1400" height="1054">
<div><h2>Named for the sugar that sweetens the cup</h2>
<p>Misri is crystallized rock sugar, stirred into chai and passed around after meals across South Asia. Misree Chai brings that ritual to Jersey City and Jackson Heights, alongside the milk teas, crepes and bowls our neighbors keep coming back for.</p></div></div></div></section>
<section class="sec-pad" id="rewards" style="padding-top:0;scroll-margin-top:var(--hh)"><div class="wrap"><div class="app"><div><h2><a href="rewards.html">Join our Rewards Program</a></h2>
<p>Download the Misree Chai app to order ahead, earn rewards on every visit, and hear about new drinks first.</p></div>
<div class="stores">{store_btn(APP_STORE, "Download on the", "App Store")}{store_btn(PLAY_STORE, "Get it on", "Google Play")}</div></div></div></section>
<section class="sec-pad" style="padding-top:0"><div class="wrap"><div class="panel"><div class="shead"><h2>Visit</h2><a href="visit.html">Map</a></div>{loc_cards()}</div></div></section>
</main>{footer()}'''
    return page("Misree Chai", "Misree Chai: chai, kulfi milk tea, crepes and bowls in Jersey City and Jackson Heights. Order online for pickup.", body, True)

QV = '''<div class="sheet" id="qv" hidden role="dialog" aria-modal="true" aria-labelledby="qv-t"><div class="box"><button class="close" type="button" aria-label="Close">✕</button><img src="" alt="">
<div class="in"><h3 id="qv-t"></h3><p class="price"></p><p class="desc"></p></div><div class="bar"><a class="btn block" href="order.html">Order for pickup</a></div></div></div>'''

MENU_BANNERS = {"drinks": "milk-tea-pour", "crepes": "crepe-griddle", "bowls": "nutella-acai-bowl", "bakery": "bun-maska"}

def item_row(n, p, im, d, attrs, add=False):
    extra = '<span class="add" aria-hidden="true">+</span><span class="qtyb" hidden></span>' if add else ""
    return (f'<button class="row" type="button" {attrs}><span class="txt"><span class="n">{n}</span>{f"<small>{d}</small>" if d else ""}<span class="p">${p}</span></span>'
            f'<span class="ph"><img src="{sm(im)}" alt="" loading="lazy" width="84" height="84">{extra}</span></button>')

def build_menu():
    chips = "".join(f'<a href="#{g}">{name}</a>' for g, name, _ in GROUPS)
    secs = ""
    for g, name, slugs in GROUPS:
        lists = ""
        for sl in slugs:
            c = BYSLUG[sl]
            sub = f'<h3 class="msub" id="{sl}">{c["name"]}</h3>' if len(slugs) > 1 else ""
            rows = "".join(f'<li><button class="mi" type="button" data-qv data-title="{esc(n)}" data-price="${p}" data-img="{img(im)}" data-desc="{esc(d)}">'
                           f'<span class="mt"><span class="n">{n}</span><span class="dots"></span><span class="p">${p}</span></span>{f"<small>{d}</small>" if d else ""}</button></li>' for n, p, im, d in c["items"])
            lists += f'{sub}<ul class="mlist">{rows}</ul>'
        count = sum(len(BYSLUG[sl]["items"]) for sl in slugs)
        secs += (f'<section class="mgroup" id="{g}" data-sec><div class="mban"><img src="{img(MENU_BANNERS[g])}" alt="" loading="lazy" width="1400" height="1054"><div><h2>{name}</h2><span>{count} items</span></div></div>'
                 f'{lists}</section>')
    body = f'''{header("menu")}<main>
<div class="phead"><div class="wrap"><h1>Menu</h1><p>Served at both cafes. Tap any item to see a photo.</p></div></div>
<nav class="chips" aria-label="Menu sections"><div class="wrap">{chips}</div></nav>
<div class="wrap">{secs}
<p class="note">Prices are from the cafe's online ordering menu and may differ in store.</p>
<div class="endcta"><a class="btn" href="order.html">Order for pickup</a></div></div></main>
{footer()}{QV}'''
    return page("Menu · Misree Chai", "The full Misree Chai menu: drinks, crepes, bowls and bakery.", body)

def build_order():
    items = []
    secs = ""
    for c in CATS:
        rows = ""
        for n, p, im, d in c["items"]:
            iid = slug(n)
            items.append(dict(id=iid, name=n, price=float(p), img=img(im), desc=d, opts=OPTIONS[c["opts"]]))
            rows += item_row(n, p, im, d, f'data-add="{iid}" aria-label="{esc(n)}, ${p}"', add=True)
        secs += f'<section class="osec" id="o-{c["slug"]}" data-sec><h2>{c["name"]}</h2><div class="ogrid">{rows}</div></section>'
    stores = [dict(id=L["id"], name=L["name"], line1=L["line1"], tax=L["tax"], lat=L["lat"], lng=L["lng"]) for L in LOCATIONS]
    data = json.dumps(dict(items=items, stores=stores)).replace("</", "<\\/")
    seg = "".join(f'<button type="button" data-store="{L["id"]}" aria-pressed="false"><b>{L["name"]}</b><span>{L["line1"]}</span></button>' for L in LOCATIONS)
    chips = "".join(f'<a href="#o-{c["slug"]}">{c["name"]}</a>' for c in CATS)
    body = f'''{header("order")}<main class="opage">
<section class="obar"><div class="wrap"><div><h1>Order online</h1><p class="demo">Demo preview. Orders aren't sent to the cafe and no card is charged.</p>
<button class="psum" id="psum" type="button" aria-haspopup="dialog">{PIN}<span><b id="ps-store"></b><span id="ps-meta"></span></span><em>Change</em></button></div>
<div class="ocontrols" id="pick" role="dialog" aria-label="Pickup details"><h3 class="phd">Pickup details</h3>
<div><span class="lbl">Pick up from</span><div class="seg" role="group" aria-label="Pickup location">{seg}</div></div>
<label><span class="lbl">Pickup time</span><select id="pickup"><option>ASAP</option></select></label>
<button class="btn block" id="pdone" type="button">Done</button></div></div></section>
<nav class="chips" aria-label="Order sections"><div class="wrap">{chips}</div></nav>
<div class="wrap olayout"><nav class="oside" aria-label="Menu sections">{chips}</nav><div class="omenu">{secs}</div>
<aside class="cart" id="cart" aria-label="Your order"><header><h2 id="c-title">Your order</h2><button class="x" type="button" aria-label="Close order">✕</button></header>
<div class="body" id="c-body"></div><div class="foot" id="c-foot"></div></aside></div></main>
<div class="scrim" id="scrim" hidden></div>
<button class="cartbar" id="cartbar" type="button" hidden><span class="ct" id="cb-count"></span><span>View order</span><span id="cb-total"></span></button>
<div class="sheet" id="sheet" hidden role="dialog" aria-modal="true" aria-labelledby="s-name"><div class="box"><button class="close" type="button" aria-label="Close">✕</button><img src="" alt="">
<div class="in"><h3 id="s-name"></h3><p class="price" id="s-price"></p><p class="desc" id="s-desc"></p><div id="s-opts"></div>
<label class="field" style="margin-top:20px">Special instructions<textarea id="s-note" rows="2" placeholder="Optional"></textarea></label></div>
<div class="bar"><div class="step"><button type="button" id="s-minus" aria-label="Fewer">−</button><span id="s-qty">1</span><button type="button" id="s-plus" aria-label="More">+</button></div>
<button class="btn" type="button" id="s-add">Add to order</button></div></div></div>
<div id="toast" class="toast" hidden role="status"></div>
<script type="application/json" id="menu-data">{data}</script>
{footer()}'''
    return page("Order Online · Misree Chai", "Order Misree Chai online for pickup in Jersey City or Jackson Heights.", body, extra_js=ORDER_JS)

def build_visit():
    strip = "".join(f'<img src="{sm(n)}" alt="" loading="lazy" width="520" height="650">' for n in ["cafe-interior", "chai-cheers", "masala-chai", "triple-chocolate-crepe", "taro-milk-tea", "bun-maska"])
    L0 = LOCATIONS[0]
    tabs = "".join(f'<button type="button" role="tab" class="loc-tab" aria-selected="{"true" if i == 0 else "false"}" data-loc="{L["id"]}" data-embed="{L["embed"]}" data-dir="{L["dir"]}" '
                   f'data-l1="{esc(L["line1"])}" data-l2="{esc(L["line2"])}" data-phone="{L["phone"]}" data-name="{L["name"]}">{L["name"]}</button>' for i, L in enumerate(LOCATIONS))
    body = f'''{header("visit")}<main>
<div class="phead"><div class="wrap"><h1>Visit</h1><p>Two cafes, one menu. Pick a location for the map and directions.</p></div></div>
<div class="wrap"><div class="ltabs" role="tablist" aria-label="Choose a location">{tabs}</div>
<div class="bigmap"><div class="map-fallback"><img src="{sm("cafe-interior")}" alt=""><span>The live Google Map loads here on the published site.</span></div>
<iframe id="loc-map" src="{L0["embed"]}" title="Google Map showing Misree Chai" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
<div class="card mapinfo"><div><h3 id="loc-name">Misree Chai · {L0["name"]}</h3><p id="loc-l1">{L0["line1"]}, {L0["line2"]}</p><p id="loc-meta">Open daily · {L0["phone"]}</p></div>
<div class="acts"><a class="btn sec" id="loc-dir" href="{L0["dir"]}" target="_blank" rel="noopener">Directions</a><a class="btn" id="loc-order" href="order.html?store={L0["id"]}">Order pickup</a></div></div></div>
<section class="sec-pad"><div class="wrap"><div class="panel"><div class="shead"><h2>Inside Misree</h2><a href="{INSTA}" target="_blank" rel="noopener">Instagram</a></div><div class="rail strip">{strip}</div></div></div></section>
</main>{footer()}'''
    return page("Visit · Misree Chai", "Find Misree Chai in Jersey City and Jackson Heights: maps and directions.", body)


def build_rewards():
    steps = [("1", "Get the app", "Download the Misree Chai app and create your free account."),
             ("2", "Order or check in", "Order ahead in the app, or show it at the counter when you pay."),
             ("3", "Earn rewards", "Every visit counts toward rewards you can use at either cafe.")]
    st = "".join(f'<li><span class="num">{n}</span><div><h3>{t}</h3><p>{d}</p></div></li>' for n, t, d in steps)
    body = f'''{header("rewards")}<main>
<div class="phead"><div class="wrap"><h1>Rewards</h1><p>Join our Rewards Program through the Misree Chai app.</p></div></div>
<section class="sec-pad" style="padding-top:16px"><div class="wrap rwrap">
<div class="panel rhero"><img src="{img("chai-cheers")}" alt="Two glasses of chai raised over bun maska and a crepe" width="1400" height="1054">
<div><h2>Every cup brings you closer to the next one</h2><p>Order ahead, skip the line, earn rewards on every visit, and hear about new drinks first.</p>
<div class="stores">{store_btn(APP_STORE, "Download on the", "App Store")}{store_btn(PLAY_STORE, "Get it on", "Google Play")}</div></div></div>
<div class="panel"><h2>How it works</h2><ol class="steps">{st}</ol></div>
<div class="promo"><div><h2>Hungry now?</h2><p>Order on the website for pickup at Jersey City or Jackson Heights.</p></div><a class="btn" href="order.html">Start an order</a></div>
</div></section>
</main>{footer()}'''
    return page("Rewards · Misree Chai", "Join the Misree Chai Rewards Program: get the app, order ahead and earn rewards at both cafes.", body)


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
for name, fn in [("index.html", build_index), ("menu.html", build_menu), ("order.html", build_order), ("visit.html", build_visit), ("rewards.html", build_rewards)]:
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(fn())
print("built", OUT)
