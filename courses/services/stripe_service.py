import stripe
from environs import env

stripe.api_key = env("STRIPE_API_KEY")


def create_stripe_product(name):
    product = stripe.Product.create(name=name)
    return product.id


def create_stripe_price(product_id, amount_in_cents):
    price = stripe.Price.create(
        product=product_id, unit_amount=amount_in_cents, currency="rub"
    )
    return price.id


def create_checkout_session(price_id, success_url, cancel_url):
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


def get_checkout_session_status(session_id):
    session = stripe.checkout.Session.retrieve(session_id)
    return session.payment_status
