const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.handler = async function(event) {
  // Only allow POST
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  try {
    const { paymentMethodId, firstName, lastName, email, tier, preferredSlot, timezone, country } = JSON.parse(event.body);

    if (!paymentMethodId || !email) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Missing required fields' })
      };
    }

    // Create Stripe Customer
    const customer = await stripe.customers.create({
      name: `${firstName} ${lastName}`,
      email: email,
      payment_method: paymentMethodId,
      metadata: {
        tier: tier || 'Standard',
        preferredSlot: preferredSlot || '',
        timezone: timezone || '',
        country: country || 'US',
        source: 'jovens_yoga_trial'
      }
    });

    // Set as default payment method
    await stripe.customers.update(customer.id, {
      invoice_settings: { default_payment_method: paymentMethodId }
    });

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customerId: customer.id,
        success: true
      })
    };

  } catch (err) {
    console.error('Stripe error:', err.message);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message })
    };
  }
};
