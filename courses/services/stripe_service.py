from typing import Tuple

import stripe

from config import settings

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(name: str) -> str:
    product = stripe.Product.create(name=name)
    return product.id


def create_stripe_price(product_id: str, amount_in_kop: int) -> str:
    price = stripe.Price.create(
        product=product_id, unit_amount=amount_in_kop, currency="rub"
    )
    return price.id


def create_checkout_session(price_id: str, success_url: str, cancel_url: str) -> Tuple[str, str]:
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.id, session.url


def get_checkout_session_status(session_id: str) -> str:
    session = stripe.checkout.Session.retrieve(session_id)
    return session.payment_status
