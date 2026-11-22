import pytest

from shop import create_app

ACCOUNT = {"name": "Ada", "email": "ada@example.test", "password": "Example123"}


@pytest.fixture
def client():
    return create_app().test_client()


@pytest.fixture
def auth(client):
    assert client.post("/api/users/register", json=ACCOUNT).status_code == 201
    token = client.post("/api/users/login", json=ACCOUNT).json["token"]
    return {"Authorization": f"Bearer {token}"}


def test_accounts(client, auth):
    assert client.post("/api/users/register", json=ACCOUNT).status_code == 409
    assert client.post("/api/users/register", json={}).status_code == 400
    assert client.post("/api/users/login", json={**ACCOUNT, "password": "wrong"}).status_code == 401
    assert client.get("/api/cart", headers=auth).json == []


def test_catalog(client):
    assert client.get("/api/products?q=tee").json[0]["title"] == "Classic Tee"
    assert client.get("/api/products/tee").status_code == 200
    assert client.get("/api/products/no-item").status_code == 404


def test_cart(client, auth):
    assert client.get("/api/cart").status_code == 401
    assert client.post("/api/cart/add", headers=auth, json={"productId": "absent"}).status_code == 400
    item = {"productId": "tee", "size": "M", "quantity": 2}
    assert client.post("/api/cart/add", headers=auth, json=item).status_code == 201
    result = client.get("/api/cart", headers=auth).json[0]
    assert result["quantity"] == 2
    assert client.delete(f"/api/cart/remove/{result['_id']}", headers=auth).status_code == 204
    assert client.get("/api/cart", headers=auth).json == []


def test_order(client, auth):
    address = {"shippingAddress": "10 Test Street"}
    assert client.post("/api/orders/create", headers=auth, json=address).status_code == 400
    item = {"productId": "tee", "size": "M", "quantity": 1}
    client.post("/api/cart/add", headers=auth, json=item)
    assert client.post("/api/orders/create", headers=auth, json={}).status_code == 400
    result = client.post("/api/orders/create", headers=auth, json=address)
    assert result.status_code == 201
    assert result.json["totalPrice"] == 20
    assert client.get("/api/orders/get", headers=auth).json == [result.json]
    assert client.get("/api/cart", headers=auth).json == []


def test_login_normalizes_email(client, auth):
    response = client.post("/api/users/login", json={**ACCOUNT, "email": " ADA@EXAMPLE.TEST "})
    assert response.status_code == 200
    assert response.json["token"] != auth["Authorization"].removeprefix("Bearer ")


def test_invalid_cart_size(client, auth):
    response = client.post("/api/cart/add", headers=auth, json={
        "productId": "tee", "size": "XXXL", "quantity": 1,
    })
    assert response.status_code == 400
    assert client.get("/api/cart", headers=auth).json == []


def test_cart_is_isolated_by_account(client, auth):
    client.post("/api/cart/add", headers=auth, json={"productId": "tee", "size": "M", "quantity": 1})
    other = {**ACCOUNT, "email": "other@example.test"}
    assert client.post("/api/users/register", json=other).status_code == 201
    token = client.post("/api/users/login", json=other).json["token"]
    assert client.get("/api/cart", headers={"Authorization": f"Bearer {token}"}).json == []
    assert len(client.get("/api/cart", headers=auth).json) == 1


def test_unauthorized_order_is_rejected(client):
    assert client.post("/api/orders/create", json={"shippingAddress": "10 Test Street"}).status_code == 401
    assert client.get("/api/orders/get", headers={"Authorization": "Bearer missing"}).status_code == 401
