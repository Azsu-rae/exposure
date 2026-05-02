"""
Deterministic payment simulator. Replaces the Chargily integration so the
service can run with no third-party dependency.

  CARD payments: a fake checkout URL is minted and the payment is moved
                 straight to HELD (escrow). In a real system the move to
                 HELD would happen on a webhook callback.
  CASH payments: stay PENDING until delivery confirms collection.
"""

import secrets

from .models import Payment


def _fake_checkout_url(payment: Payment) -> str:
    token = secrets.token_urlsafe(16)
    return f"https://sim.exposure.local/checkout/{payment.id}?t={token}"


def process_new_payment(payment: Payment) -> Payment:
    if payment.method == Payment.Method.CARD:
        payment.checkout_url = _fake_checkout_url(payment)
        payment.status = Payment.Status.HELD
    else:
        payment.status = Payment.Status.PENDING
    payment.save(update_fields=["checkout_url", "status"])
    return payment
