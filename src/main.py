from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)


def add(a, b):
    return a+b

def subtract(a, b):
    return a-b



# Configure logging - use accessible path
log_dir = os.path.expanduser('~/flask-app/logs')
# Alternative: log_dir = '/var/log/flask-app'  # if you created with proper permissions

# Create log directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'flask-app.log')

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5)
log_handler.setFormatter(log_formatter)

app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

# Also add console handler for development
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
app.logger.addHandler(console_handler)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'flask_http_request_count_total',
    'Total HTTP Request Count',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'flask_http_request_duration_seconds',
    'HTTP Request Latency',
    ['method', 'endpoint']
)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Calculate request latency
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.method, request.path).observe(latency)
    
    # Count requests
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    
    # Log request
    app.logger.info(f'{request.method} {request.path} {response.status_code} {latency:.4f}s')
    
    return response

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/')
def hello():
    app.logger.info('Hello endpoint called')
    return jsonify({"message": "Hello, World!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)