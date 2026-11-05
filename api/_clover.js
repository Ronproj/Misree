// Shared Clover helpers for the order API (Vercel serverless functions).
// Each cafe is its own Clover merchant, so every call names a store and uses that store's keys.
// Keys live in Vercel environment variables, never in the page. See README "Online ordering".

const ENV = process.env.CLOVER_ENV === 'production' ? 'production' : 'sandbox';
const HOSTS = {
  sandbox: { api: 'https://apisandbox.dev.clover.com', ecom: 'https://scl-sandbox.dev.clover.com', sdk: 'https://checkout.sandbox.dev.clover.com/sdk.js' },
  production: { api: 'https://api.clover.com', ecom: 'https://scl.clover.com', sdk: 'https://checkout.clover.com/sdk.js' },
}[ENV];

// Store id (as used by the site) -> environment variable prefix.
const STORES = { 'jersey-city': 'CLOVER_JC', 'jackson-heights': 'CLOVER_JH' };

function storeConfig(id) {
  const p = STORES[id];
  if (!p) return null;
  const e = process.env;
  return {
    id,
    merchantId: e[p + '_MERCHANT_ID'],
    apiToken: e[p + '_API_TOKEN'],           // REST API token (menu and orders)
    ecomPublic: e[p + '_ECOM_PUBLIC_KEY'],   // Ecommerce public key, used by the card fields in the browser
    ecomPrivate: e[p + '_ECOM_PRIVATE_KEY'], // Ecommerce private key, used to charge on the server
  };
}
const canMenu = s => !!(s && s.merchantId && s.apiToken);
const canPay = s => canMenu(s) && !!(s.ecomPublic && s.ecomPrivate);

class CloverError extends Error {
  constructor(status, body, where) { super(`Clover ${where} failed (${status})`); this.status = status; this.body = body; }
}

async function call(url, opts, where) {
  const r = await fetch(url, opts);
  const text = await r.text();
  let body; try { body = text ? JSON.parse(text) : {}; } catch { body = { raw: text }; }
  if (!r.ok) throw new CloverError(r.status, body, where);
  return body;
}
const rest = (s, path, init = {}) => call(`${HOSTS.api}/v3/merchants/${s.merchantId}${path}`, {
  ...init, headers: { Authorization: `Bearer ${s.apiToken}`, 'Content-Type': 'application/json', Accept: 'application/json', ...(init.headers || {}) },
}, 'REST ' + path.split('?')[0]);

// Clover list endpoints page with limit/offset; read every page.
async function all(s, path) {
  const out = [];
  for (let offset = 0; ; offset += 1000) {
    const sep = path.includes('?') ? '&' : '?';
    const page = await rest(s, `${path}${sep}limit=1000&offset=${offset}`);
    out.push(...(page.elements || []));
    if (!page.elements || page.elements.length < 1000) return out;
  }
}

// Menu: categories in Clover's order, each with its visible, available items and their option groups.
async function loadMenu(s) {
  const [cats, items, groups] = await Promise.all([
    all(s, '/categories'),
    all(s, '/items?expand=categories,modifierGroups'),
    all(s, '/modifier_groups?expand=modifiers'),
  ]);
  return normalizeMenu(cats, items, groups);
}

function normalizeMenu(cats, items, groups) {
  const G = new Map(groups.map(g => [g.id, g]));
  const sellable = items.filter(i => !i.hidden && i.available !== false && i.priceType !== 'VARIABLE');
  const opts = i => ((i.modifierGroups && i.modifierGroups.elements) || []).map(r => G.get(r.id)).filter(Boolean)
    .map(g => ({
      id: g.id, name: g.name,
      min: g.minRequired || 0, max: g.maxAllowed || 0, // 0 means no limit
      mods: ((g.modifiers && g.modifiers.elements) || []).filter(m => m.available !== false).map(m => ({ id: m.id, name: m.name, price: m.price || 0 })),
    })).filter(g => g.mods.length);
  const shape = i => ({ id: i.id, name: i.name, price: i.price || 0, desc: i.alternateName || '', opts: opts(i) });
  const sorted = [...cats].sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0));
  const out = sorted.map(c => ({
    id: c.id, name: c.name,
    items: sellable.filter(i => ((i.categories && i.categories.elements) || []).some(x => x.id === c.id)).map(shape),
  })).filter(c => c.items.length);
  return { categories: out };
}

// Cart lines from the browser -> an atomic order cart. Prices and tax always come from Clover, never the browser.
// Quantity is sent as repeated line items, which keeps each line's modifiers and note on the kitchen ticket.
function buildCart(body) {
  const lines = Array.isArray(body.lines) ? body.lines : [];
  if (!lines.length || lines.length > 40) throw new Error('Your order needs between 1 and 40 lines.');
  const lineItems = [];
  for (const l of lines) {
    const qty = Math.floor(Number(l.qty));
    if (typeof l.itemId !== 'string' || !(qty >= 1 && qty <= 20)) throw new Error('One of the items in your order is not valid.');
    const mods = (Array.isArray(l.modIds) ? l.modIds : []).filter(m => typeof m === 'string').slice(0, 20);
    const note = typeof l.note === 'string' ? l.note.slice(0, 200) : '';
    for (let k = 0; k < qty; k++) {
      lineItems.push({ item: { id: l.itemId }, ...(mods.length && { modifications: mods.map(id => ({ modifier: { id } })) }), ...(note && { note }) });
    }
  }
  if (lineItems.length > 60) throw new Error('That order is too large to place online. Please call the cafe.');
  const name = String(body.name || '').trim().slice(0, 60);
  const phone = String(body.phone || '').trim().slice(0, 30);
  const pickup = String(body.pickup || 'ASAP').trim().slice(0, 40);
  const orderCart = {
    lineItems,
    title: `ONLINE PICKUP: ${name}`.slice(0, 127),
    note: `Online order for pickup ${pickup}. ${name}${phone ? ', ' + phone : ''}`.slice(0, 255),
  };
  if (process.env.CLOVER_ORDER_TYPE_ID) orderCart.orderType = { id: process.env.CLOVER_ORDER_TYPE_ID };
  return { orderCart, name, phone, pickup };
}

const quote = (s, orderCart) => rest(s, '/atomic_order/checkouts', { method: 'POST', body: JSON.stringify({ orderCart }) });
const createOrder = (s, orderCart) => rest(s, '/atomic_order/orders', { method: 'POST', body: JSON.stringify({ orderCart }) });
const deleteOrder = (s, id) => rest(s, `/orders/${id}`, { method: 'DELETE' });
const printOrder = (s, id) => rest(s, '/print_event', { method: 'POST', body: JSON.stringify({ orderRef: { id } }) });

// Charge the card token against the Clover order, so the payment is attached to that order.
const payOrder = (s, orderId, token, ip, email) => call(`${HOSTS.ecom}/v1/orders/${orderId}/pay`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${s.ecomPrivate}`, 'Content-Type': 'application/json', Accept: 'application/json', ...(ip && { 'x-forwarded-for': ip }) },
  body: JSON.stringify({ source: token, ecomind: 'ecom', ...(email && { email }) }),
}, 'payment');

function send(res, status, data, cache) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', cache || 'no-store');
  res.end(JSON.stringify(data));
}
async function readJson(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') return JSON.parse(req.body);
  let raw = ''; for await (const c of req) { raw += c; if (raw.length > 50000) throw new Error('Request too large'); }
  return raw ? JSON.parse(raw) : {};
}
// Log the details for us; show the customer a plain message.
function fail(res, err, msg) {
  console.error(err && err.message, err && err.body ? JSON.stringify(err.body).slice(0, 2000) : '');
  send(res, err instanceof CloverError ? 502 : 400, { error: err instanceof CloverError ? msg : (err && err.message) || msg });
}

module.exports = { ENV, HOSTS, STORES, storeConfig, canMenu, canPay, CloverError, loadMenu, normalizeMenu, buildCart, quote, createOrder, deleteOrder, printOrder, payOrder, send, readJson, fail };
