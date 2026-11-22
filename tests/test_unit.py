import pytest

from shop import find_products, order_total, valid_account


@pytest.mark.parametrize(("query", "ids"), [
    ("", ["tee", "cap"]), (" TEE ", ["tee"]), ("CAP", ["cap"]), ("missing", []),
])
def test_search(query, ids):
    assert [item["_id"] for item in find_products(query)] == ids


@pytest.mark.parametrize(("name", "email", "password", "valid"), [
    ("Ada", "ada@example.test", "Example123", True),
    (" ", "ada@example.test", "Example123", False),
    ("Ada", "invalid", "Example123", False),
    ("Ada", "ada@example.test", "short", False),
])
def test_account_validation(name, email, password, valid):
    assert valid_account(name, email, password) is valid


@pytest.mark.parametrize(("cart", "total"), [
    ([], 0), ([{"price": 20, "quantity": 1}], 20),
    ([{"price": 20, "quantity": 2}], 40),
    ([{"price": 20, "quantity": 2}, {"price": 12, "quantity": 1}], 52),
])
def test_total(cart, total):
    assert order_total(cart) == total
