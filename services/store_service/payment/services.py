from chargily_pay import ChargilyClient
from django.conf import settings
from chargily_pay.entity import Checkout
client = ChargilyClient(
    secret=settings.CHARGILY_SECRET,
    key=settings.CHARGILY_KEY,
    url=settings.CHARGILY_URL,
)


def create_checkout(payment):

    checkout_data = Checkout(  # ← use the dataclass, not a dict
        amount=payment.amount,
        currency="dzd",
        success_url="http://localhost:8000/success",
        failure_url="http://localhost:8000/failure",
        webhook_endpoint="https://lasonya-mispacked-berserkly.ngrok-free.dev/api/payment/webhook/",
    )

    response = client.create_checkout(checkout=checkout_data)

    payment.entity_id = response["id"]
    payment.checkout_url = response["checkout_url"]
    payment.save()

    return payment
def transfer_to_seller(ccp, amount):
    """
    Sends money from YOUR Chargily account to the seller's ccp account.
    Called automatically when payment is released.
    """
    response = client.transfer({
        "to_account": ccp,   # seller's Chargily ID
        "amount": amount,
        "currency": "dzd",
    })
    return response