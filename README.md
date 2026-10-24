# Misree Chai website

Static site for Misree Chai, 789 Newark Ave, Jersey City.

- `index.html`: home page (video hero, categories, app/rewards, visit)
- `menu.html`: full menu (Drinks, Crepes, Bowls, Bakery)
- `assets/`: photos and simple photo layout

There is no build step. Deploy the repo root as a static site (Vercel: Framework Preset "Other", no build command, output directory `.`).

To change menu items, prices or links, edit `tools/build.py` and regenerate:

```
python3 tools/build.py .
```

Set `APP_STORE` and `PLAY_STORE` in `tools/build.py` once the app links are known.
