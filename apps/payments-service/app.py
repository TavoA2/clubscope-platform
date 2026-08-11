from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import requests
import os
import time
import uuid

app = Flask(__name__)

PRODUCTS_SERVICE_URL = os.environ.get("PRODUCTS_SERVICE_URL", "http://products-service")

REQUEST_COUNT = Counter(
    "payments_service_requests_total", "Total requests received", ["endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "payments_service_request_duration_seconds", "Request latency in seconds", ["endpoint"]
)
UPSTREAM_ERRORS = Counter(
    "payments_service_upstream_errors_total", "Errors calling products-service", ["reason"]
)


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/payments", methods=["POST"])
def create_payment():
    start = time.time()
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        REQUEST_COUNT.labels(endpoint="/payments", status="400").inc()
        return jsonify({"error": "product_id is required"}), 400

    try:
        resp = requests.get(f"{PRODUCTS_SERVICE_URL}/products", timeout=3)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        UPSTREAM_ERRORS.labels(reason=type(e).__name__).inc()
        REQUEST_COUNT.labels(endpoint="/payments", status="502").inc()
        return jsonify({"error": "products-service unavailable", "detail": str(e)}), 502

    products = resp.json()
    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        REQUEST_COUNT.labels(endpoint="/payments", status="404").inc()
        return jsonify({"error": f"product {product_id} not found"}), 404

    total = round(product["price"] * quantity, 2)
    payment = {
        "payment_id": str(uuid.uuid4()),
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "total": total,
        "status": "approved",
    }

    REQUEST_LATENCY.labels(endpoint="/payments").observe(time.time() - start)
    REQUEST_COUNT.labels(endpoint="/payments", status="201").inc()
    return jsonify(payment), 201


@app.route("/metrics")
def metrics():
    from flask import Response
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
