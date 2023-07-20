import os
import time
import redis
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest

load_dotenv()

app = Flask(__name__)
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")

db = redis.Redis(host=redis_host, port=redis_port)

request_count = Counter('requests', 'Total Request Count')
latency = Histogram('latency_seconds', 'Request latency')
cache_hits = Gauge('cache_hits', 'Total Cache Hits')


@app.route('/get/<key>', methods=['GET'])
def get(key):
    request_count.inc()
    if key in db:
        cache_hits.inc()

        start_time = time.time()
        value = db.get(key).decode('utf-8')
        latency.observe(time.time() - start_time)
        if value:
            return jsonify({'value': value})

    return jsonify({}), 404


@app.route('/set', methods=['POST'])
def set():
    request_count.inc()
    data = request.get_json()
    key = data['key']
    value = data['value']
    db.set(key, value)
    return jsonify({'message': 'key set'})


@app.route('/search', methods=['GET'])
def search():
    request_count.inc()
    args = request.args
    keys = []

    if 'prefix' in args:
        cache_hits.inc()
        prefix = args['prefix'].encode('utf-8')
        start_time = time.time()
        keys = [key.decode('utf-8')
                for key in db.keys() if key.startswith(prefix)]
        latency.observe(time.time() - start_time)

    elif 'suffix' in args:
        cache_hits.inc()
        suffix = args['suffix'].encode('utf-8')
        start_time = time.time()
        keys = [key.decode('utf-8')
                for key in db.keys() if key.endswith(suffix)]
        latency.observe(time.time() - start_time)

    values = [val.decode('utf-8') for val in db.mget(keys)]
    result = dict(zip(keys, values))

    return jsonify(result)


@app.route('/delete', methods=['POST'])
def delete():
    request_count.inc()
    data = request.get_json()
    key = data['key']
    if key in db:
        cache_hits.inc()

        start_time = time.time()
        db.delete(key)
        latency.observe(time.time() - start_time)
        return jsonify({'message': 'key deleted'})

    return jsonify({'message': 'key not found'})


@app.route('/health')
def health():
    start_time = time.time()

    try:
        db.ping()
        response_time = time.time() - start_time
        status = "UP"
    except redis.exceptions.ConnectionError:
        status = "DOWN"
        response_time = -1

    health = {
        'status': status,
        'responseTime': response_time,
        'timestamp': int(start_time)
    }

    return jsonify(health)


@app.route('/metrics')
def metrics():
    return generate_latest()
