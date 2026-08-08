from flask import Flask, jsonify, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import socket
import time

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "hello_service_requests_total",
    "Total requests received",
    ["endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "hello_service_request_duration_seconds",
    "Request latency in seconds",
    ["endpoint"]
)

@app.route("/")
def hello():
    start = time.time()
    response = jsonify({
        "message": "Hello from Clubscope Platform",
        "hostname": socket.gethostname(),
        "version": os.environ.get("APP_VERSION", "dev")
    })
    REQUEST_LATENCY.labels(endpoint="/").observe(time.time() - start)
    REQUEST_COUNT.labels(endpoint="/", status="200").inc()
    return response

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
