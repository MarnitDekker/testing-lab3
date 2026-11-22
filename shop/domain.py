import re

PRODUCTS = [
    {"_id": "tee", "title": "Classic Tee", "price": 20},
    {"_id": "cap", "title": "Canvas Cap", "price": 12},
]


def find_products(query):
    needle = query.strip().casefold()
    return [
        {
            **product, "images": ["/catalog.svg"], "sizes": ["S", "M", "L", "XL"],
            "brand": "Clothify", "discount": 0, "originalPrice": product["price"], "rating": 5, "reviews": "1",
            "description": "Sample catalogue item",
        }
        for product in PRODUCTS if needle in product["title"].casefold()
    ]


def valid_account(name, email, password):
    return bool(name.strip() and re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) and len(password) >= 8)


def order_total(cart):
    return sum(item["price"] * item["quantity"] for item in cart)

