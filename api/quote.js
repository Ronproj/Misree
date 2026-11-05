// POST /api/quote {store, lines} -> Clover's own subtotal, tax and total for the cart, shown at checkout.
const C = require('./_clover');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return C.send(res, 405, { error: 'Use POST.' });
  try {
    const body = await C.readJson(req);
    const s = C.storeConfig(body.store);
    if (!C.canMenu(s)) return C.send(res, 503, { error: "Online ordering isn't switched on for this cafe yet." });
    const q = await C.quote(s, C.buildCart(body).orderCart);
    C.send(res, 200, { subtotal: q.subtotal ?? null, tax: q.totalTaxAmount ?? q.taxAmount ?? q.tax ?? null, total: q.total ?? null });
  } catch (e) { C.fail(res, e, "We couldn't price your order. Please try again."); }
};
