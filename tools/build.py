"""Misree Chai static site generator (photo + video edition).
Usage: python3 build2.py OUTDIR [--artifact]
Pages reference media at assets/img/<name>.jpg and assets/video/<name>.mp4."""
import os, sys, html, json

OUT = sys.argv[1]
ARTIFACT = "--artifact" in sys.argv

ADDRESS = "789 Newark Ave, Jersey City, NJ 07306"
PHONE = "(856) 210-2029"
MAPS = "https://www.google.com/maps/search/?api=1&query=Misree+Chai+789+Newark+Ave+Jersey+City+NJ"
DIRECTIONS = "https://www.google.com/maps/dir/?api=1&destination=Misree+Chai%2C+789+Newark+Ave%2C+Jersey+City%2C+NJ+07306"
MAP_EMBED = "https://www.google.com/maps?q=Misree+Chai%2C+789+Newark+Ave%2C+Jersey+City%2C+NJ+07306&z=16&output=embed"
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

def slug(s):
    return s.lower().replace(" ", "-")

# Menu data from the cafe's DoorDash / Uber Eats listings and misreechai.com search snippets.
CATS = [
    dict(slug="chai", name="Chai & Coffee", kicker="The heart of the house", video="chai-pour", poster="chai-pour",
         intro="Slow-brewed chai and South Indian coffee, poured hot and sweetened the old way.",
         items=[("Masala Chai", "4.00", "masala-chai", ""), ("Zafrani Chai", "3.49", "zafrani-chai", ""),
                ("South Indian Coffee", "4.00", "south-indian-coffee", "")]),
    dict(slug="kulfi", name="Kulfi Milk Tea", kicker="House signature", video="milk-tea", poster="milk-tea-pour",
         intro="Creamy milk tea built around the flavors of kulfi.",
         items=[("Falooda Kulfi", "7.49", "falooda-kulfi", "Falooda-inspired creamy milk tea."),
                ("Mango Kulfi", "7.49", "mango-kulfi", ""), ("Pista Kulfi", "7.49", "pista-kulfi", "")]),
    dict(slug="teas", name="Milk & Fruit Teas", kicker="Iced and bright", video="milk-tea", poster="milk-tea-pour",
         intro="Classic milk teas and fruit teas, shaken over ice.",
         items=[("Classic Milk Tea", "6.49", "classic-milk-tea", ""), ("Taro Milk Tea", "6.49", "taro-milk-tea", ""),
                ("Strawberry Milk Tea", "6.49", "strawberry-milk-tea", ""), ("Mango Fruit Tea", "5.49", "mango-fruit-tea", ""),
                ("Strawberry Fruit Tea", "5.49", "strawberry-fruit-tea", ""), ("Peach Fruit Tea", "5.49", "peach-fruit-tea", ""),
                ("Lychee Refresher", "5.99", "lychee-refresher", "")]),
    dict(slug="crepes", name="Crepes", kicker="Folded to order", video="crepe", poster="crepe-griddle",
         intro="Sweet crepes off the griddle, generously filled and finished with drizzle.",
         items=[("Triple Chocolate Crepe", "14.00", "triple-chocolate-crepe", "Kinder Bueno, Ferrero, Nutella and chocolate chips."),
                ("Nutella Crepe", "13.99", "nutella-crepe", ""), ("Royal Pistachio Crepe", "13.99", "royal-pistachio-crepe", ""),
                ("Fudge Brownie Crepe", "12.99", "fudge-brownie-crepe", ""), ("Oreo Crepe", "13.99", "oreo-crepe", ""),
                ("Mix Berries Crepe", "13.99", "mix-berries-crepe", "")]),
    dict(slug="bowls", name="Bowls", kicker="Cold and loaded", video="interior", poster="cafe-interior",
         intro="Acai and protein bowls stacked with fruit, nuts and drizzle.",
         items=[("Nutella Acai Bowl", "12.99", "nutella-acai-bowl", ""), ("Almond Lover Bowl", "13.99", "almond-lover-bowl", ""),
                ("Coconut Honey Bowl", "13.99", "coconut-honey-bowl", ""), ("Protein Bowl", "12.99", "protein-bowl", "")]),
    dict(slug="bakery", name="Bakery", kicker="With your chai", video="chai-pour", poster="chai-cheers",
         intro="Buttery bakes made for dunking.",
         items=[("Bun Maska", "4.49", "bun-maska", ""), ("Butter Croissant", "4.00", "butter-croissant", ""),
                ("Nutella Croissant", "5.00", "nutella-croissant", "")]),
]

def img(name): return f"assets/img/{name}.jpg"
def vid(name): return f"assets/video/{name}.mp4"

CSS = r"""
/* Layout: cinematic teahouse. Full-bleed video bands in deep peacock, saffron accents, photo-led menu. */
:root{
  --paper:#f5f0e8; --surface:#fffaf2; --ink:#1c2523; --muted:#5b6662; --line:#e2d7c7;
  --night:#0c1f1d; --night-ink:#f4ecdf; --saffron:#d08a22; --saffron-ink:#1b1206; --rose:#c25a6c;
  --scrim:rgba(8,20,19,.62); --card-shadow:0 1px 2px rgba(28,37,35,.06),0 12px 32px rgba(28,37,35,.08);
  --display:"Gloock","Iowan Old Style",Georgia,serif;
  --body:"Hanken Grotesk",system-ui,-apple-system,"Segoe UI",sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --paper:#0e1716; --surface:#142120; --ink:#efe7da; --muted:#a6b0ab; --line:#26332f;
  --saffron:#e3a24a; --card-shadow:0 1px 2px rgba(0,0,0,.3),0 12px 32px rgba(0,0,0,.35); color-scheme:dark}}
:root[data-theme="dark"]{
  --paper:#0e1716; --surface:#142120; --ink:#efe7da; --muted:#a6b0ab; --line:#26332f;
  --saffron:#e3a24a; --card-shadow:0 1px 2px rgba(0,0,0,.3),0 12px 32px rgba(0,0,0,.35); color-scheme:dark}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font:400 17px/1.6 var(--body);-webkit-font-smoothing:antialiased}
a{color:inherit}
img,video{max-width:100%;display:block}
.wrap{max-width:1200px;margin:0 auto;padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px))}
h1,h2,h3{font-family:var(--display);font-weight:400;line-height:1.04;text-wrap:balance;margin:0}
.eyebrow{font-size:.76rem;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:var(--saffron);margin:0 0 14px}
:focus-visible{outline:3px solid var(--saffron);outline-offset:3px;border-radius:6px}
.btn{display:inline-flex;align-items:center;gap:8px;text-decoration:none;font:600 .95rem var(--body);padding:13px 22px;border-radius:999px;background:var(--saffron);color:var(--saffron-ink);border:0;cursor:pointer;transition:transform .2s, box-shadow .2s}
.btn:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(208,138,34,.35)}
.btn.ghost{background:rgba(255,255,255,.08);color:var(--night-ink);box-shadow:inset 0 0 0 1.5px rgba(244,236,223,.6);backdrop-filter:blur(6px)}

/* header: transparent over video, solid after scroll */
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:30;background:var(--night)}
.top{position:fixed;left:0;right:0;top:env(safe-area-inset-top,0px);z-index:20;color:var(--night-ink);transition:background .3s, box-shadow .3s}
.top.solid{background:rgba(12,31,29,.92);backdrop-filter:blur(10px);box-shadow:0 1px 0 rgba(255,255,255,.06)}
.top .wrap{display:flex;align-items:center;gap:20px;padding-block:16px}
.brand{text-decoration:none;font-family:var(--display);font-size:1.5rem;white-space:nowrap}
.brand span{color:var(--saffron)}
.nav{display:flex;gap:22px;margin-left:auto;font-size:.93rem}
.nav a{text-decoration:none;opacity:.85;padding:4px 0;border-bottom:1.5px solid transparent}
.nav a:hover,.nav a[aria-current]{opacity:1;border-color:var(--saffron)}
.menu-btn{display:none;margin-left:auto;background:none;border:0;color:inherit;font:600 .95rem var(--body);cursor:pointer;padding:12px 4px 12px 16px;min-height:44px}
.top .btn{padding:10px 18px}
@media (max-width:900px){
  .menu-btn{display:block}.top .btn{display:none}
  .nav{position:fixed;inset:0;top:0;flex-direction:column;justify-content:center;align-items:center;gap:18px;padding:0 max(24px, env(safe-area-inset-right,0px)) 0 max(24px, env(safe-area-inset-left,0px));text-align:center;background:var(--night);font:400 clamp(1.6rem,8vw,2.2rem)/1.15 var(--display);opacity:0;pointer-events:none;transition:opacity .25s;margin:0}
  .nav a{padding:6px 0}
  .nav .nav-order{display:inline-flex;font:600 1rem var(--body);margin-top:12px;padding:14px 26px;border:0}
  .nav.open{opacity:1;pointer-events:auto}
  .nav .close{position:absolute;top:calc(18px + env(safe-area-inset-top,0px));right:max(16px, env(safe-area-inset-right,0px));font:600 .9rem var(--body)}
}
@media (min-width:901px){.nav .close,.nav .nav-order{display:none}}

/* video bands */
.vband{position:relative;overflow:hidden;background:var(--night);color:var(--night-ink);isolation:isolate}
.vband video,.vband .poster{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:-2}
.vband::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,rgba(8,20,19,.55) 0%,var(--scrim) 55%,rgba(8,20,19,.85) 100%)}
.hero .wrap{min-height:min(92vh,860px);display:flex;flex-direction:column;justify-content:flex-end;padding-block:140px 72px}
.hero h1{font-size:clamp(3.4rem,11vw,9rem);letter-spacing:-.015em}
.hero h1 em{font-style:normal;color:var(--saffron)}
.hero .lede{font-size:clamp(1.05rem,2vw,1.3rem);max-width:36ch;opacity:.92;margin:18px 0 30px}
.ctas{display:flex;gap:12px;flex-wrap:wrap}
.vtoggle{position:absolute;right:max(16px, env(safe-area-inset-right,0px));bottom:16px;z-index:2;background:rgba(0,0,0,.35);color:#fff;border:1px solid rgba(255,255,255,.3);border-radius:999px;font:600 .8rem var(--body);padding:12px 16px;cursor:pointer;backdrop-filter:blur(6px)}
.scroll-cue{font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;opacity:.7;margin-top:48px}

.ticker{background:var(--saffron);color:var(--saffron-ink);overflow:hidden;white-space:nowrap;font:400 1.25rem var(--display)}
.ticker div{display:inline-flex;gap:40px;padding:14px 0;animation:tick 40s linear infinite}
.ticker span::after{content:"✦";margin-left:40px;font-size:.8rem;vertical-align:middle}
@keyframes tick{to{transform:translateX(-50%)}}

.facts{display:grid;grid-template-columns:repeat(3,1fr);background:var(--surface);border-bottom:1px solid var(--line)}
.facts>div{padding:24px;min-width:0}
.facts>div+div{border-left:1px solid var(--line)}
.facts b{display:block;font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);font-weight:600;margin-bottom:4px}
@media (max-width:760px){.facts{grid-template-columns:1fr}.facts>div+div{border-left:0;border-top:1px solid var(--line)}}

section.pad{padding-block:96px}
.sec-head{display:flex;justify-content:space-between;align-items:end;gap:24px;flex-wrap:wrap;margin-bottom:40px}
.sec-head h2{font-size:clamp(2.3rem,5.5vw,4rem)}
.sec-head p{max-width:44ch;color:var(--muted);margin:0}

/* category mosaic */
.mosaic{display:grid;grid-template-columns:repeat(6,1fr);grid-auto-rows:220px;gap:14px}
.mtile{position:relative;overflow:hidden;border-radius:20px;text-decoration:none;color:#fff;isolation:isolate;grid-column:span 2}
.mtile:nth-child(1){grid-column:span 3;grid-row:span 2}.mtile:nth-child(2){grid-column:span 3;grid-row:span 1}
.mtile:nth-child(3){grid-column:span 3}
.mtile img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:-2;transition:transform .7s cubic-bezier(.2,.7,.2,1)}
.mtile::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,transparent 35%,rgba(0,0,0,.72))}
.mtile:hover img{transform:scale(1.07)}
.mtile .t{position:absolute;left:22px;right:22px;bottom:18px;display:flex;justify-content:space-between;align-items:end;gap:12px}
.mtile h3{font-size:clamp(1.6rem,3vw,2.3rem)}
.mtile small{font-size:.85rem;opacity:.85;white-space:nowrap}
@media (max-width:820px){.mosaic{grid-template-columns:1fr 1fr;grid-auto-rows:200px}.mtile,.mtile:nth-child(n){grid-column:span 1;grid-row:span 1}.mtile:nth-child(1){grid-column:span 2}}
@media (max-width:480px){.mosaic{grid-template-columns:1fr}.mtile:nth-child(1){grid-column:span 1}}

/* story split */
.story{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center}
.story .photos{position:relative;aspect-ratio:1/1}
.story .photos img{position:absolute;border-radius:20px;object-fit:cover;box-shadow:var(--card-shadow)}
.story .photos img:first-child{inset:0 18% 18% 0;width:82%;height:82%}
.story .photos img:last-child{right:0;bottom:0;width:52%;height:52%;border:6px solid var(--paper)}
.story h2{font-size:clamp(2.2rem,5vw,3.5rem)}
.story p{color:var(--muted);max-width:50ch}
@media (max-width:820px){.story{grid-template-columns:1fr}}

/* printed-menu layout */
.mtabs{position:sticky;top:calc(env(safe-area-inset-top,0px) + 66px);z-index:10;background:var(--paper);border-bottom:1px solid var(--line)}
.mtabs .wrap{display:flex;gap:6px;overflow-x:auto;padding-block:10px;scrollbar-width:none}
.mtabs a{flex:0 0 auto;text-decoration:none;font:600 .9rem var(--body);padding:12px 18px;border-radius:999px;color:var(--muted);transition:background .2s,color .2s}
.mtabs a[aria-current="true"]{background:var(--ink);color:var(--paper)}
.msec{display:grid;grid-template-columns:minmax(0,340px) minmax(0,1fr);gap:64px;padding-block:72px;border-top:1px solid var(--line);scroll-margin-top:120px}
.msec:first-child{border-top:0}
.msec aside{position:sticky;top:150px;align-self:start}
.msec aside img{border-radius:20px;aspect-ratio:4/5;object-fit:cover;width:100%;margin-top:22px;box-shadow:var(--card-shadow)}
.msec h2{font-size:clamp(2.4rem,5vw,3.6rem)}
.msec aside p{color:var(--muted);margin:10px 0 0}
.msec aside a{display:inline-block;margin-top:14px;color:var(--saffron);font-weight:600;font-size:.9rem;text-decoration:none}
@media (max-width:860px){.msec{grid-template-columns:1fr;gap:20px;padding-block:52px}.msec aside{position:static}.msec aside img{display:none}}
.mlist{display:flex;flex-direction:column}
.mi{display:grid;grid-template-columns:72px minmax(0,1fr);gap:18px;align-items:center;padding:16px 4px;border:0;border-bottom:1px solid var(--line);background:none;text-align:left;color:inherit;font:inherit;cursor:pointer;width:100%;border-radius:0;transition:background .2s}
.mi:hover{background:var(--surface)}
.mi img{width:72px;height:72px;border-radius:50%;object-fit:cover;transition:transform .4s}
.mi:hover img{transform:scale(1.08) rotate(-3deg)}
.mi .l{display:flex;align-items:baseline;gap:10px}
.mi .n{font:400 clamp(1.2rem,2.2vw,1.5rem)/1.2 var(--display)}
.mi .dots{flex:1;min-width:20px;border-bottom:2px dotted var(--line);transform:translateY(-5px)}
.mi .p{font-weight:700;font-variant-numeric:tabular-nums;color:var(--saffron)}
.mi small{display:block;color:var(--muted);font-size:.9rem;margin-top:2px}
.mi .view{font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);opacity:0;transition:opacity .2s}
.mi:hover .view{opacity:1}
@media (max-width:520px){.mi{grid-template-columns:56px minmax(0,1fr);gap:14px}.mi img{width:56px;height:56px}.mi .view{display:none}}
.menu-hero .wrap{min-height:min(52vh,460px);display:flex;flex-direction:column;justify-content:flex-end;padding-block:130px 48px}
.menu-hero h1{font-size:clamp(3.4rem,10vw,7.5rem)}
.note{font-size:.85rem;color:var(--muted);margin-top:22px}
.plain{max-width:760px;margin:0 auto;text-align:center}
.plain h2{font-size:clamp(2.4rem,6vw,4rem);margin-bottom:28px}
.plain ul{list-style:none;margin:0;padding:0;text-align:left;border-top:1.5px solid var(--ink)}
.plain li button{display:block;width:100%;background:none;border:0;border-bottom:1px solid var(--line);padding:18px 2px;text-align:left;color:inherit;font:inherit;cursor:pointer}
.plain li button:hover .n{color:var(--saffron)}
.plain .l{display:flex;align-items:baseline;gap:12px}
.plain .n{font:400 clamp(1.3rem,2.6vw,1.7rem)/1.2 var(--display);transition:color .2s}
.plain .dots{flex:1;min-width:20px;border-bottom:2px dotted var(--line);transform:translateY(-5px)}
.plain .p{font-weight:700;font-variant-numeric:tabular-nums}
.plain small{display:block;color:var(--muted);font-size:.92rem;margin-top:4px}
.msec-plain{padding-block:72px 8px;scroll-margin-top:130px}
.msec-plain + .msec-plain{border-top:1px solid var(--line);margin-top:56px}
.plain h3{font:600 .82rem var(--body);letter-spacing:.18em;text-transform:uppercase;color:var(--saffron);text-align:left;margin:36px 0 8px;scroll-margin-top:140px}
.plain h3 + ul{border-top-width:1px}
.rewards{background:var(--night);color:var(--night-ink)}
#rewards,#visit{scroll-margin-top:64px}
.rewards .wrap{display:grid;grid-template-columns:1fr minmax(0,360px);gap:56px;align-items:center;padding-block:96px}
.rewards h2{font-size:clamp(2.4rem,6vw,4.2rem)}
.rewards .rw-copy p{opacity:.85;max-width:42ch}
.stores{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}
.store{display:inline-flex;flex-direction:column;justify-content:center;min-width:160px;min-height:52px;padding:10px 20px;border-radius:14px;background:var(--night-ink);color:var(--night);text-decoration:none;line-height:1.15;transition:transform .2s}
.store:hover{transform:translateY(-2px)}
.store small{font-size:.78rem;opacity:.8}
.store b{font:600 1.2rem var(--body)}
.store[aria-disabled="true"]{opacity:.55;cursor:default}
.phone{justify-self:center;width:min(280px,70vw);aspect-ratio:9/19;border-radius:40px;padding:10px;background:#1a1a1a;box-shadow:0 30px 60px rgba(0,0,0,.45),inset 0 0 0 2px rgba(255,255,255,.12)}
.phone .screen{position:relative;height:100%;border-radius:32px;overflow:hidden}
.phone img{width:100%;height:100%;object-fit:cover}
.app-ui{position:absolute;left:0;right:0;bottom:0;padding:22px 18px;background:linear-gradient(transparent,rgba(0,0,0,.8));color:#fff;display:flex;flex-direction:column;gap:2px}
.app-ui b{font:400 1.5rem var(--display)}
.app-ui span{font-size:.8rem;opacity:.85}
.app-ui i{display:block;height:40px;border-radius:999px;background:var(--saffron);margin-top:12px}
@media (max-width:820px){.rewards .wrap{grid-template-columns:1fr;gap:36px;padding-block:72px}.phone{width:min(200px,55vw)}}
.menu-hero .lede{font-size:1.15rem;max-width:40ch;opacity:.9;margin:14px 0 0}
.bigmap{position:relative;height:min(70vh,620px);min-height:380px;border-radius:24px 24px 0 0;overflow:hidden;background:var(--night);isolation:isolate}
.bigmap iframe,.bigmap .map-fallback{position:absolute;inset:0;width:100%;height:100%;border:0}
.bigmap .map-fallback img{width:100%;height:100%;object-fit:cover;opacity:.45}
.bigmap .map-fallback span{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);color:var(--night-ink);background:rgba(8,20,19,.7);padding:12px 18px;border-radius:12px;font-size:.9rem;text-align:center;max-width:80%}
.mapbar{display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;background:var(--night);color:var(--night-ink);padding:24px 28px;border-radius:0 0 24px 24px}
.mapbar h3{font-size:clamp(1.3rem,3vw,1.8rem)}
.mapbar p{margin:4px 0 0;opacity:.8;font-size:.95rem}
.mapbar .eyebrow{margin:0 0 6px;opacity:1}
@media (max-width:600px){.bigmap{height:420px;min-height:0}.mapbar .btn{width:100%;justify-content:center}}
.tlink{color:var(--saffron);font-weight:600;text-decoration:none;display:inline-block;padding:10px 0;margin-top:auto}
.cta-row{display:flex;justify-content:center;margin-top:36px}

/* quick view */
.qv{position:fixed;inset:0;z-index:50;display:grid;place-items:center;padding:max(16px, env(safe-area-inset-top,0px)) max(16px, env(safe-area-inset-right,0px)) max(16px, env(safe-area-inset-bottom,0px)) max(16px, env(safe-area-inset-left,0px));background:rgba(6,14,13,.7);backdrop-filter:blur(6px)}
.qv .box{background:var(--surface);color:var(--ink);border-radius:22px;overflow:hidden;max-width:880px;width:100%;display:grid;grid-template-columns:1.2fr 1fr;max-height:100%;animation:pop .25s ease-out}
.qv .box img{width:100%;height:100%;object-fit:cover;min-height:280px}
.qv .info{padding:32px;display:flex;flex-direction:column;gap:12px;overflow:auto}
.qv h3{font-size:2.2rem}
.qv .price{font:700 1.4rem var(--body);color:var(--saffron)}
.qv .x{align-self:flex-end;background:none;border:1px solid var(--line);color:var(--ink);border-radius:999px;padding:6px 12px;cursor:pointer;font:600 .8rem var(--body)}
.qv .order{margin-top:auto;display:flex;gap:10px;flex-wrap:wrap}
.qv .order .btn.alt{background:var(--paper);color:var(--ink);box-shadow:inset 0 0 0 1.5px var(--line)}
@media (max-width:700px){.qv .box{grid-template-columns:1fr}.qv .box img{min-height:0;aspect-ratio:4/3}}
@keyframes pop{from{transform:scale(.96);opacity:.6}}

/* gallery strip */
.strip{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:10px}
.strip img{flex:0 0 auto;width:min(360px,78vw);aspect-ratio:4/5;object-fit:cover;border-radius:18px;scroll-snap-align:start}

/* visit */
.visit .wrap{display:grid;grid-template-columns:1.2fr 1fr;gap:48px;align-items:end;padding-block:120px}
.visit h2{font-size:clamp(2.6rem,6.5vw,4.8rem)}
.visit dl{display:grid;grid-template-columns:auto 1fr;gap:12px 24px;margin:0;background:rgba(8,20,19,.55);backdrop-filter:blur(8px);padding:28px;border-radius:20px;border:1px solid rgba(255,255,255,.12)}
.visit dt{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;opacity:.7;padding-top:5px}
.visit dd{margin:0;font-size:1.05rem}
.visit dd a{display:inline-block;padding:8px 0}
@media (max-width:820px){.visit .wrap{grid-template-columns:1fr}}
footer{padding-block:28px;font-size:.85rem;color:var(--muted)}
footer .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}

/* category page */
.cat-hero .wrap{min-height:min(70vh,640px);display:flex;flex-direction:column;justify-content:flex-end;padding-block:130px 56px}
.cat-hero h1{font-size:clamp(3.2rem,9vw,7rem)}
.cat-hero p.lede{font-size:1.2rem;max-width:40ch;opacity:.9;margin:14px 0 0}
.crumbs{font-size:.85rem;opacity:.8;margin-bottom:16px}
.crumbs a{text-decoration:none}
.feature{display:grid;grid-template-columns:1.3fr 1fr;gap:40px;align-items:center;margin-bottom:56px}
.feature img{border-radius:22px;aspect-ratio:4/3;object-fit:cover;width:100%;box-shadow:var(--card-shadow)}
.feature h2{font-size:clamp(2.2rem,4.5vw,3.4rem)}
.feature .price{font:700 1.3rem var(--body);color:var(--saffron);margin:10px 0 18px;display:block}
@media (max-width:820px){.feature{grid-template-columns:1fr}}
.pager{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:56px;padding-top:28px;border-top:1px solid var(--line)}
.pager a{text-decoration:none;display:flex;flex-direction:column;gap:2px}
.pager a span{font-size:.75rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.pager a b{font-family:var(--display);font-weight:400;font-size:1.7rem}
.pager a:last-child{text-align:right;margin-left:auto}

/* scroll reveal: content is visible at rest, motion only adds a lift */
@media (prefers-reduced-motion:no-preference){
  .rv{transition:transform .8s cubic-bezier(.2,.7,.2,1)}
  .js .rv:not(.in){transform:translateY(28px)}
}
@media (prefers-reduced-motion:reduce){.ticker div{animation:none}html{scroll-behavior:auto}}
"""

JS = r"""
document.documentElement.classList.add('js');
const bar=document.querySelector('.top');
const onScroll=()=>bar&&bar.classList.toggle('solid',scrollY>40);
addEventListener('scroll',onScroll,{passive:true});onScroll();
const nav=document.querySelector('.nav');
document.querySelectorAll('[data-nav]').forEach(b=>b.addEventListener('click',()=>nav.classList.toggle('open')));
nav&&nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>nav.classList.remove('open')));
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{rootMargin:'0px 0px -8% 0px'});
document.querySelectorAll('.rv').forEach(el=>{if(el.getBoundingClientRect().top<innerHeight)el.classList.add('in');else io.observe(el)});
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
document.querySelectorAll('.vband').forEach(band=>{
  const v=band.querySelector('video'),t=band.querySelector('.vtoggle');if(!v)return;
  if(reduce){v.removeAttribute('autoplay');v.pause()}
  const sync=()=>{if(t)t.textContent=v.paused?'Play video':'Pause video'};
  v.addEventListener('play',sync);v.addEventListener('pause',sync);sync();
  t&&t.addEventListener('click',()=>v.paused?v.play():v.pause());
  v.addEventListener('error',()=>v.remove(),true);
});
// menu tabs scrollspy
const tabs=document.querySelectorAll('.mtabs a');
if(tabs.length){
  const map=new Map([...tabs].map(a=>[a.getAttribute('href').slice(1),a]));
  const spy=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){tabs.forEach(t=>t.removeAttribute('aria-current'));const a=map.get(e.target.id);if(a){a.setAttribute('aria-current','true');a.scrollIntoView({block:'nearest',inline:'center'})}}}),{rootMargin:'-45% 0px -50% 0px'});
  document.querySelectorAll('[data-sec]').forEach(s=>spy.observe(s));
}
// quick view
const qv=document.getElementById('qv');
if(qv){
  const box=qv.querySelector('.box');let last=null;
  const close=()=>{qv.hidden=true;last&&last.focus()};
  document.querySelectorAll('[data-item]').forEach(c=>c.addEventListener('click',()=>{
    last=c;const d=c.dataset;
    qv.querySelector('img').src=d.img;qv.querySelector('img').alt=d.title;
    qv.querySelector('h3').textContent=d.title;qv.querySelector('.price').textContent=d.price;
    qv.querySelector('.cat').textContent=d.catname;qv.querySelector('.desc').textContent=d.desc||'';
    qv.hidden=false;qv.querySelector('.x').focus();}));
  qv.addEventListener('click',e=>{if(!box.contains(e.target))close()});
  qv.querySelector('.x').addEventListener('click',close);
  addEventListener('keydown',e=>{if(e.key==='Escape'&&!qv.hidden)close()});
}
"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gloock&family=Hanken+Grotesk:wght@400;500;600;700&display=swap">'

def page(title, desc, body, is_index=False):
    head = (f'<title>{title}</title><meta name="claude:viewport-fit-sides" content="cover">'
            f'<meta name="description" content="{html.escape(desc)}"><meta property="og:image" content="{img("chai-pour")}">{FONTS}<style>{CSS}</style>')
    tail = f'<script>{JS}</script>'
    if ARTIFACT and is_index:
        return head + body + tail
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'{head}</head><body>{body}{tail}</body></html>')

def header(current=None):
    links = f'<a href="index.html"{" aria-current=page" if current is None else ""}>Home</a><a href="menu.html"{" aria-current=page" if current=="menu" else ""}>Menu</a>' + f'<a href="index.html#rewards">Join our Rewards Program</a><a href="visit.html"{" aria-current=page" if current=="visit" else ""}>Visit</a><a class="btn nav-order" href="{DOORDASH}" target="_blank" rel="noopener">Order Online</a>'
    return (f'<header class="top"><div class="wrap"><a class="brand" href="index.html">Misree <span>Chai</span></a>'
            f'<nav class="nav" aria-label="Menu categories"><button class="menu-btn close" data-nav type="button">Close</button>{links}</nav>'
            f'<button class="menu-btn" data-nav type="button" aria-label="Open menu">Menu</button>'
            f'<a class="btn" href="{DOORDASH}" target="_blank" rel="noopener">Order Online</a></div></header>')

def vband_media(video, poster):
    return (f'<img class="poster" src="{img(poster)}" alt="" aria-hidden="true">'
            f'<video autoplay muted loop playsinline preload="metadata" poster="{img(poster)}" aria-hidden="true"><source src="{vid(video)}" type="video/mp4"></video>'
            f'<button class="vtoggle" type="button">Pause video</button>')

def visit():
    return f'''<section class="vband visit" id="visit">{vband_media("interior", "cafe-interior")}<div class="wrap">
<div><p class="eyebrow">Visit</p><h2>Pull up a chair on Newark Ave.</h2><div class="ctas" style="margin-top:28px"><a class="btn" href="visit.html">Plan your visit</a><a class="btn ghost" href="{DIRECTIONS}" target="_blank" rel="noopener">Get directions</a></div></div>
<dl><dt>Address</dt><dd>{ADDRESS}</dd><dt>Phone</dt><dd>{PHONE}</dd><dt>Hours</dt><dd>Open daily, morning until late.<br><a href="{MAPS}" target="_blank" rel="noopener">Today's hours on Google Maps</a></dd>
<dt>Delivery</dt><dd><a href="{DOORDASH}" target="_blank" rel="noopener">DoorDash</a> · <a href="{UBER}" target="_blank" rel="noopener">Uber Eats</a></dd></dl></div></section>'''

def footer():
    return (f'<footer><div class="wrap"><span>Misree Chai · {ADDRESS}</span>'
            f'<span>Prices from the cafe\'s online ordering menu and may change. Photos are styled representations.</span></div></footer>')

QV = f'''<div class="qv" id="qv" hidden role="dialog" aria-modal="true" aria-label="Item details"><div class="box"><img src="" alt=""><div class="info">
<button class="x" type="button">Close</button><span class="cat eyebrow"></span><h3></h3><span class="price"></span><p class="desc" style="color:var(--muted);margin:0"></p>
<div class="order"><a class="btn" href="{DOORDASH}" target="_blank" rel="noopener">Order on DoorDash</a></div></div></div></div>'''

def row(c, item):
    n, p, im, d = item
    return (f'<button class="mi" type="button" data-item data-title="{html.escape(n)}" data-price="${p}" data-img="{img(im)}" '
            f'data-catname="{html.escape(c["name"])}" data-desc="{html.escape(d)}" data-page="{c["slug"]}.html">'
            f'<img src="{img(im)}" alt="" loading="lazy"><span><span class="l"><span class="n">{n}</span><span class="dots"></span><span class="p">${p}</span></span>'
            f'{f"<small>{d}</small>" if d else ""}</span></button>')

def plain_row(c, item):
    n, p, im, d = item
    return (f'<li><button type="button" data-item data-title="{html.escape(n)}" data-price="${p}" data-img="{img(im)}" '
            f'data-catname="{html.escape(c["name"])}" data-desc="{html.escape(d)}" data-page="{c["slug"]}.html">'
            f'<span class="l"><span class="n">{n}</span><span class="dots"></span><span class="p">${p}</span></span>{f"<small>{d}</small>" if d else ""}</button></li>')

def menu_section(c, link=True):
    rows = "".join(row(c, it) for it in c["items"])
    more = f'<a href="{c["slug"]}.html">Open the {c["name"]} page →</a>' if link else ""
    return (f'<section class="msec" id="{c["slug"]}"><aside><p class="eyebrow">{c["kicker"]}</p><h2>{c["name"]}</h2><p>{c["intro"]}</p>{more}'
            f'<img src="{img(c["items"][0][2])}" alt="{html.escape(c["items"][0][0])}" loading="lazy"></aside><div class="mlist">{rows}</div></section>')

GROUPS = [("drinks", "Drinks", "Hot and iced", ["chai", "kulfi", "teas"]),
          ("crepes", "Crepes", "Folded to order", ["crepes"]),
          ("bowls", "Bowls", "Cold and loaded", ["bowls"]),
          ("bakery", "Bakery", "With your chai", ["bakery"])]
BYSLUG = {c["slug"]: c for c in CATS}
GROUP_OF = {s: g for g, _, _, ss in GROUPS for s in ss}

def build_menu():
    tabs = "".join(f'<a href="#{g}">{name}</a>' for g, name, _, _ in GROUPS)
    secs = ""
    for g, name, kicker, slugs in GROUPS:
        lists = ""
        for sl in slugs:
            c = BYSLUG[sl]
            sub = f'<h3 id="{sl}">{c["name"]}</h3>' if len(slugs) > 1 else ""
            lists += f'{sub}<ul>{"".join(plain_row(c, it) for it in c["items"])}</ul>'
        secs += f'<section class="plain msec-plain" id="{g}" data-sec><p class="eyebrow">{kicker}</p><h2>{name}</h2>{lists}</section>'
    body = f'''{header("menu")}
<section class="vband menu-hero">{vband_media("milk-tea", "milk-tea-pour")}<div class="wrap">
<p class="crumbs"><a href="index.html">Home</a> / Menu</p><p class="eyebrow">Served daily on Newark Ave</p><h1>The Menu</h1></div></section>
<nav class="mtabs" aria-label="Menu sections"><div class="wrap" style="justify-content:center">{tabs}</div></nav>
<div class="wrap">{secs}<p class="note" style="text-align:center">Tap an item to see a photo. Prices are from the cafe's online ordering menu and may differ in store.</p>
<div class="ctas" style="justify-content:center;margin-top:24px"><a class="btn" href="{DOORDASH}" target="_blank" rel="noopener">Order on DoorDash</a></div></div>
<div style="height:88px"></div>
{visit()}{footer()}{QV}'''
    return page("Menu · Misree Chai", "The full Misree Chai menu: drinks, crepes, bowls and bakery.", body)

def build_visit():
    strip = "".join(f'<img src="{img(n)}" alt="" loading="lazy">' for n in ["cafe-interior", "chai-cheers", "masala-chai", "triple-chocolate-crepe", "taro-milk-tea", "bun-maska"])
    body = f'''{header("visit")}
<section class="vband menu-hero">{vband_media("interior", "cafe-interior")}<div class="wrap">
<p class="crumbs"><a href="index.html">Home</a> / Visit</p><p class="eyebrow">Journal Square, Jersey City</p><h1>Come say hi.</h1>
<p class="lede">Pull up a chair for a glass of chai, or grab a kulfi milk tea and a crepe to go.</p></div></section>
<section class="pad"><div class="wrap">
<div class="bigmap"><div class="map-fallback"><img src="{img("cafe-interior")}" alt=""><span>The live Google Map loads here on the published site.</span></div>
<iframe src="{MAP_EMBED}" title="Google Map showing Misree Chai at 789 Newark Ave, Jersey City" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
<div class="mapbar"><div><p class="eyebrow">Misree Chai</p><h3>{ADDRESS}</h3><p>Open daily, morning until late · {PHONE}</p></div>
<a class="btn" href="{DIRECTIONS}" target="_blank" rel="noopener">Get directions in Google Maps →</a></div>
</div></section>
<section class="pad" style="padding-top:0"><div class="wrap"><div class="sec-head rv"><div><p class="eyebrow">Inside Misree</p><h2>Warm light, hot chai.</h2></div><p><a class="tlink" href="{INSTA}" target="_blank" rel="noopener">Follow @misreechai on Instagram →</a></p></div><div class="strip">{strip}</div></div></section>
{footer()}{QV}'''
    return page("Visit · Misree Chai", "Find Misree Chai at 789 Newark Ave, Jersey City: map, directions, hours and contact.", body)

def build_index():
    tiles = "".join(f'<a class="mtile rv" href="menu.html#{c["slug"]}"><img src="{img(c["items"][0][2])}" alt="" loading="lazy"><div class="t"><h3>{c["name"]}</h3><small>{len(c["items"])} items →</small></div></a>' for c in CATS)
    names = [it[0] for c in CATS for it in c["items"]]
    tick = "".join(f"<span>{n}</span>" for n in names[:14]) * 2
    strip = "".join(f'<img src="{img(n)}" alt="" loading="lazy">' for n in ["chai-cheers", "falooda-kulfi", "triple-chocolate-crepe", "taro-milk-tea", "nutella-acai-bowl", "bun-maska", "royal-pistachio-crepe", "mango-fruit-tea"])
    body = f'''{header()}
<section class="vband hero">{vband_media("chai-pour", "chai-pour")}<div class="wrap">
<p class="eyebrow">Chai house · Journal Square, Jersey City</p><h1>Misree <em>Chai</em></h1>
<p class="lede">Masala chai, kulfi milk tea, crepes and acai bowls, made fresh on Newark Avenue.</p>
<div class="ctas"><a class="btn" href="menu.html">See the menu</a><a class="btn ghost" href="{DOORDASH}" target="_blank" rel="noopener">Order for delivery</a></div>
<p class="scroll-cue">Scroll ↓</p></div></section>
<div class="ticker" aria-hidden="true"><div>{tick}</div></div>
<div class="facts"><div><b>Where</b>{ADDRESS}</div><div><b>Call</b>{PHONE}</div><div><b>When</b>Open daily, morning until late</div></div>
<section class="pad"><div class="wrap"><div class="sec-head rv"><div><p class="eyebrow">The menu</p><h2>Six ways to take a break.</h2></div><p>Pick a category, or open the full menu.</p></div><div class="mosaic">{tiles}</div><div class="cta-row"><a class="btn" href="menu.html">View the full menu</a></div></div></section>
<section class="pad" style="background:var(--surface)"><div class="wrap story"><div class="photos rv"><img src="{img("misri")}" alt="Misri rock sugar beside a glass of chai" loading="lazy"><img src="{img("masala-chai")}" alt="Masala chai" loading="lazy"></div>
<div class="rv"><p class="eyebrow">Why "Misree"</p><h2>Named for the sugar that sweetens the cup.</h2><p>Misri is crystallized rock sugar, stirred into chai and passed around after meals across South Asia. Misree Chai brings that ritual to Jersey City, next to the milk teas, crepes and bowls the neighborhood keeps coming back for.</p>
<a class="btn" href="menu.html#chai" style="margin-top:12px">Start with chai</a></div></div></section>
<section class="rewards" id="rewards"><div class="wrap"><div class="rw-copy rv"><p class="eyebrow">The Misree Chai app</p><h2>Join our Rewards Program.</h2>
<p>Download the Misree Chai app to order ahead, collect rewards on every visit, and hear about new drinks first.</p>
<div class="stores">{store_btn(APP_STORE, "Download on the", "App Store")}{store_btn(PLAY_STORE, "Get it on", "Google Play")}</div></div>
<div class="phone rv" aria-hidden="true"><div class="screen"><img src="{img("falooda-kulfi")}" alt=""><div class="app-ui"><b>Misree Chai</b><span>Order ahead · Rewards</span><i></i></div></div></div></div></section>
<section class="pad"><div class="wrap"><div class="strip">{strip}</div></div></section>
{visit()}{footer()}{QV}'''
    return page("Misree Chai", "Misree Chai, a chai house at 789 Newark Ave in Jersey City.", body, True)

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "index.html"), "w") as fh:
    fh.write(build_index())
with open(os.path.join(OUT, "visit.html"), "w") as fh:
    fh.write(build_visit())
with open(os.path.join(OUT, "menu.html"), "w") as fh:
    fh.write(build_menu())
print("built", OUT)
