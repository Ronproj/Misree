// POST /api/order {store, lines, name, phone, pickup, token} -> creates the order in that cafe's Clover,
// charges the card against it, then prints the ticket.
// The order is created before the charge, so a declined card never leaves a paid order missing from Clover.
const C = require('./_clover');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return C.send(res, 405, { error: 'Use POST.' });
  let body, s, cart;
  try {
    body = await C.readJson(req);
    s = C.storeConfig(body.store);
    if (!C.canPay(s)) return C.send(res, 503, { error: "Online ordering isn't switched on for this cafe yet." });
    cart = C.buildCart(body);
    if (!cart.name) throw new Error('Please add your name for the order.');
    if (typeof body.token !== 'string' || !/^clv_/.test(body.token)) throw new Error('Please enter your card details.');
  } catch (e) { return C.fail(res, e, 'Something in your order is not valid.'); }

  let order;
  try { order = await C.createOrder(s, cart.orderCart); }
  catch (e) { return C.fail(res, e, "We couldn't send your order to the cafe. You have not been charged. Please try again."); }

  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  let charge;
  try { charge = await C.payOrder(s, order.id, body.token, ip); }
  catch (e) {
    // Remove the unpaid order so staff don't make it.
    try { await C.deleteOrder(s, order.id); } catch (d) { console.error('ALERT unpaid order left in Clover', s.id, order.id, d.message); }
    const declined = e.body && e.body.error && (e.body.error.message || e.body.error.code);
    console.error('payment failed', s.id, order.id, JSON.stringify(e.body || {}).slice(0, 2000));
    return C.send(res, 402, { error: declined ? `Your card didn't go through: ${declined}. You have not been charged.` : "Your card didn't go through. You have not been charged." });
  }

  // Print the kitchen ticket. A failed print doesn't undo a paid order; it's logged so we can check the printer.
  try { await C.printOrder(s, order.id); } catch (e) { console.error('ALERT paid order did not print', s.id, order.id, e.message); }

  C.send(res, 200, { ok: true, orderId: order.id, number: order.id.slice(-4).toUpperCase(), total: order.total ?? charge.amount ?? null, pickup: cart.pickup });
};
