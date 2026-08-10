from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import psycopg2
import psycopg2.extras
import os
import time

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "postgres"),
    "port": os.environ.get("DB_PORT", "5432"),
    "dbname": os.environ.get("POSTGRES_DB", "products"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
}

REQUEST_COUNT = Counter(
    "products_service_requests_total", "Total requests received", ["endpoint", "method", "status"]
)
REQUEST_LATENCY = Histogram(
    "products_service_request_duration_seconds", "Request latency in seconds", ["endpoint"]
)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            price NUMERIC(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/products", methods=["GET"])
def list_products():
    start = time.time()
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, name, price, created_at FROM products ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    REQUEST_LATENCY.labels(endpoint="/products").observe(time.time() - start)
    REQUEST_COUNT.labels(endpoint="/products", method="GET", status="200").inc()
    return jsonify([dict(r, price=float(r["price"]), created_at=r["created_at"].isoformat()) for r in rows])


@app.route("/products", methods=["POST"])
def create_product():
    start = time.time()
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")

    if not name or price is None:
        REQUEST_COUNT.labels(endpoint="/products", method="POST", status="400").inc()
        return jsonify({"error": "name and price are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", (name, price))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    REQUEST_LATENCY.labels(endpoint="/products").observe(time.time() - start)
    REQUEST_COUNT.labels(endpoint="/products", method="POST", status="201").inc()
    return jsonify({"id": new_id, "name": name, "price": price}), 201


@app.route("/metrics")
def metrics():
    from flask import Response
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
