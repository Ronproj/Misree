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

## Online ordering (Clover)

`order.html` shows a built-in demo menu until a cafe's Clover keys are set. With keys, the page loads that cafe's live menu from Clover, prices the order with Clover, takes the card with Clover's card fields, and sends the order to that cafe's Clover, where it prints.

The `api/` folder holds the server side as Vercel functions, so no secret key ever reaches the browser:

- `api/menu.js` (`GET /api/menu?store=jersey-city`): the live menu, including categories, items, and option groups with prices. It answers `{live:false}` until keys are set.
- `api/quote.js` (`POST /api/quote`): Clover's exact tax and total for a cart.
- `api/order.js` (`POST /api/order`): creates the order in Clover, charges the card against it, then prints the ticket. If the card is declined, the order is deleted, so staff never see an unpaid order.

Set these in Vercel under Project → Settings → Environment Variables, then redeploy:

| Variable | What it is |
| --- | --- |
| `CLOVER_ENV` | `sandbox` while testing, `production` for real orders |
| `CLOVER_JC_MERCHANT_ID` | Jersey City merchant ID (`C2814MP8WGP71` in production) |
| `CLOVER_JC_API_TOKEN` | Jersey City REST API token (inventory and orders) |
| `CLOVER_JC_ECOM_PUBLIC_KEY` | Jersey City Ecommerce public key (card fields) |
| `CLOVER_JC_ECOM_PRIVATE_KEY` | Jersey City Ecommerce private key (charges) |
| `CLOVER_JH_…` | The same four for Jackson Heights (merchant ID `T7P8GJV5QCR61` in production) |
| `CLOVER_ORDER_TYPE_ID` | Optional. A Clover order type such as "Online pickup" to tag web orders |

Only one cafe needs keys to go live. A cafe without keys keeps showing the demo menu.

Photos are matched to live menu items by name: "Masala Chai" uses `assets/img/masala-chai.jpg`. Items without a matching photo show the logo.
