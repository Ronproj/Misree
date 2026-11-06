// GET /api/menu?store=jersey-city -> that cafe's live menu from Clover, plus what the card fields need.
// Answers {live:false} until the store's keys are set, so the order page keeps its built-in demo menu.
const C = require('./_clover');

module.exports = async (req, res) => {
  const s = C.storeConfig(String((req.query && req.query.store) || new URL(req.url, 'http://x').searchParams.get('store') || ''));
  if (!s) return C.send(res, 400, { error: 'Unknown store.' });
  if (!C.canMenu(s)) return C.send(res, 200, { live: false }, 'public, s-maxage=60');
  try {
    const menu = await C.loadMenu(s);
    const pay = C.canPay(s) ? { sdk: C.HOSTS.sdk, key: s.ecomPublic, merchantId: s.merchantId } : null;
    // Cache briefly at Vercel's edge so a busy lunch rush doesn't hit Clover on every page view.
    C.send(res, 200, { live: true, env: C.ENV, pay, ...menu }, 'public, s-maxage=60, stale-while-revalidate=300');
  } catch (e) { C.fail(res, e, "We couldn't load the menu. Please try again in a moment."); }
};
