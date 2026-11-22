from pathlib import Path
from uuid import uuid4

from flask import Flask, abort, g, request, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash

from .domain import find_products, order_total, valid_account

__all__ = ["create_app", "find_products", "order_total", "valid_account"]


def create_app():
    app = Flask(__name__, static_folder=None)
    dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
    users, sessions, carts, orders = {}, {}, {}, {}

    @app.before_request
    def authenticate():
        if request.path.startswith(("/api/cart", "/api/orders")):
            token = request.headers.get("Authorization", "").removeprefix("Bearer ")
            g.user_id = sessions.get(token)
            if g.user_id is None:
                abort(401)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/users/register")
    def register():
        data = request.get_json() or {}
        name, email, password = (str(data.get(key, "")) for key in ("name", "email", "password"))
        email = email.strip().casefold()
        if not valid_account(name, email, password):
            return {"message": "Invalid account details"}, 400
        if email in users:
            return {"message": "Email already registered"}, 409
        users[email] = (uuid4().hex, generate_password_hash(password))
        return {"message": "Registration successful"}, 201

    @app.post("/api/users/login")
    def login():
        data = request.get_json() or {}
        user = users.get(str(data.get("email", "")).strip().casefold())
        if user is None or not check_password_hash(user[1], str(data.get("password", ""))):
            return {"message": "Invalid email or password"}, 401
        token = uuid4().hex
        sessions[token] = user[0]
        return {"token": token, "userId": user[0], "message": "Login successful"}

    @app.get("/api/products")
    def products():
        return find_products(request.args.get("q", ""))

    @app.get("/api/products/<product_id>")
    def get_product(product_id):
        product = next((p for p in find_products("") if p["_id"] == product_id), None)
        return product if product else ({"message": "Product not found"}, 404)

    @app.get("/api/cart")
    def get_cart():
        return carts.get(g.user_id, [])

    @app.post("/api/cart/add")
    def add_to_cart():
        data = request.get_json() or {}
        product = next((p for p in find_products("") if p["_id"] == data.get("productId")), None)
        quantity = data.get("quantity")
        size = data.get("size")
        if product is None or type(quantity) is not int or quantity < 1 or size not in product["sizes"]:
            return {"message": "Invalid item"}, 400
        carts.setdefault(g.user_id, []).append({
            "_id": uuid4().hex, "productId": product["_id"], "title": product["title"],
            "img1": product["images"][0], "price": product["price"], "quantity": quantity, "size": size,
        })
        return {"message": "Item added to cart"}, 201

    @app.delete("/api/cart/remove/<item_id>")
    def remove_item(item_id):
        carts[g.user_id] = [item for item in carts.get(g.user_id, []) if item["_id"] != item_id]
        return "", 204

    @app.post("/api/orders/create")
    def checkout():
        cart = carts.get(g.user_id, [])
        address = str((request.get_json() or {}).get("shippingAddress", "")).strip()
        if not cart or not address:
            return {"message": "Cart and shipping address are required"}, 400
        order = {
            "_id": uuid4().hex, "totalPrice": order_total(cart), "shippingAddress": address,
            "paymentStatus": "Pending", "orderStatus": "Pending", "products": cart,
        }
        orders.setdefault(g.user_id, []).append(order)
        carts.pop(g.user_id, None)
        return order, 201

    @app.get("/api/orders/get")
    def get_orders():
        return orders.get(g.user_id, [])

    @app.get("/<path:path>")
    @app.get("/", defaults={"path": ""})
    def frontend(path):
        if path.startswith("api/"):
            abort(404)
        if path.startswith("assets/") or path.endswith(".svg"):
            return send_from_directory(dist, path)
        return send_from_directory(dist, "index.html")

    return app
