import os
from uuid import uuid4

import pytest
from playwright.sync_api import expect

from .pages import ShopPages

PASSWORD = "Example123"


@pytest.fixture
def pages(page):
    return ShopPages(page)


@pytest.fixture
def email():
    return f"shop-{uuid4().hex}@example.test"


@pytest.fixture
def account(playwright, base_url, email):
    request = playwright.request.new_context(base_url=base_url)
    response = request.post("/api/users/register", data={
        "name": "Lab User", "email": email, "password": PASSWORD,
    })
    assert response.status == 201
    request.dispose()
    return email


def test_registration(pages, page, email):
    pages.register(email, PASSWORD)
    expect(page.get_by_role("heading", name="Login")).to_be_visible()
    pages.login(email, PASSWORD)


def test_login(pages, page, account):
    pages.login(account, PASSWORD)
    expect(page.get_by_role("button", name="Logout")).to_be_visible()


def test_search(pages, page):
    pages.search("tee")
    if os.getenv("DEMO") == "e2e":
        expect(page.get_by_role("heading", name="Intentional failure")).to_be_visible(timeout=1000)
    expect(page.get_by_role("heading", name="Classic Tee")).to_be_visible()
    expect(page.get_by_role("heading", name="Canvas Cap")).to_have_count(0)


def test_add_to_cart(pages, page, account):
    pages.login(account, PASSWORD)
    pages.add_tee()
    expect(page.get_by_role("heading", name="Classic Tee")).to_be_visible()


def test_checkout(pages, page, account):
    pages.login(account, PASSWORD)
    pages.add_tee()
    pages.order(account)
    expect(page.get_by_role("heading", name="Order Placed Successfully!")).to_be_visible()
    expect(page.get_by_text("Classic Tee", exact=True)).to_be_visible()


def test_logout(pages, page, account):
    pages.login(account, PASSWORD)
    pages.logout()
    page.goto("/cart")
    expect(page).to_have_url("/login")
