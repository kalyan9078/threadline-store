import json
import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "store.db"
app = Flask(__name__, static_folder="static")

PRODUCTS = [
    ("The Linen Set", "Essentials", 89, "Relaxed linen shirt and tailored shorts in a sun-washed oat.", "https://images.unsplash.com/photo-1598032895397-b9472444bf93?auto=format&fit=crop&w=900&q=80", "New", 1),
    ("Sculpted Blazer", "Tailoring", 148, "A softly structured layer with an effortless, borrowed-from-him cut.", "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=900&q=80", "", 1),
    ("Ribbed Tank", "Essentials", 36, "Our weighty, close-knit tank for days that call for simplicity.", "https://images.unsplash.com/photo-1605763240000-7e93b172d754?auto=format&fit=crop&w=900&q=80", "Best seller", 1),
    ("Drift Dress", "Dresses", 112, "A fluid midi dress made to follow the light and your plans.", "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?auto=format&fit=crop&w=900&q=80", "", 0),
    ("Studio Trouser", "Tailoring", 98, "High-rise wide-leg trousers cut from soft, draping twill.", "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=900&q=80", "", 0),
    ("Everyday Tee", "Essentials", 32, "The perfectly measured tee in breathable organic cotton.", "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=900&q=80", "New", 0),
]


def connection():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def initialize_database():
    db = connection()
    db.executescript((BASE_DIR / "schema.sql").read_text())
    if db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO products (name, category, price, description, image_url, badge, featured) VALUES (?, ?, ?, ?, ?, ?, ?)",
            PRODUCTS,
        )
    db.commit()
    db.close()


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/products")
def products():
    category = request.args.get("category", "All")
    db = connection()
    if category == "All":
        rows = db.execute("SELECT * FROM products ORDER BY featured DESC, id").fetchall()
    else:
        rows = db.execute("SELECT * FROM products WHERE category = ? ORDER BY id", (category,)).fetchall()
    db.close()
    return jsonify([dict(row) for row in rows])


@app.post("/api/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    name, email, items = data.get("name", "").strip(), data.get("email", "").strip(), data.get("items", [])
    if not name or "@" not in email or not isinstance(items, list) or not items:
        return jsonify({"error": "Please provide your name, email, and at least one item."}), 400
    normalized_items = []
    db = connection()
    for item in items:
        product_id = item.get("id")
        quantity = int(item.get("quantity", 0))
        product = db.execute("SELECT id, name, price FROM products WHERE id = ?", (product_id,)).fetchone()
        if not product or quantity < 1 or quantity > 20:
            db.close()
            return jsonify({"error": "Your cart is invalid."}), 400
        normalized_items.append({"id": product["id"], "name": product["name"], "price": product["price"], "quantity": quantity})
    total = sum(item["price"] * item["quantity"] for item in normalized_items)
    if total <= 0:
        db.close()
        return jsonify({"error": "Your cart is invalid."}), 400
    cursor = db.execute(
        "INSERT INTO orders (customer_name, email, items_json, total) VALUES (?, ?, ?, ?)",
        (name, email, json.dumps(normalized_items), total),
    )
    db.commit()
    order_id = cursor.lastrowid
    db.close()
    return jsonify({"message": "Order received", "order_id": order_id}), 201


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True, port=int(os.environ.get("PORT", "5001")))
