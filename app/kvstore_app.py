import os
import time
import redis
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Load the environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Redis database environment variables
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")

# create a redis instance
db = redis.Redis(host=redis_host, port=redis_port)

# metrics for prometheus monitoring
request_count = Counter('requests', 'Total Request Count')
latency = Histogram('latency_seconds', 'Request latency')
cache_hits = Gauge('cache_hits', 'Total Cache Hits')


@app.route('/get/<key>', methods=['GET'])
def get(key):
    """ Get the value of the provided key. Will return null Dict if key not present in the database.

    Args:
        key (str): Key for which the value has to be retrieved

    Returns:
        Dict: Dictionary containing the value of the provided key.
    """
    request_count.inc()
    if key in db:
        try:
            cache_hits.inc()

            start_time = time.time()

            # decode required as redis database returns data in bytes
            value = db.get(key).decode('utf-8')
            latency.observe(time.time() - start_time)
            if value:
                return jsonify({'value': value})
        except Exception as err:
            return jsonify({'error': err})

    return jsonify({}), 404


@app.route('/set', methods=['POST'])
def set():
    """ Sets the key-value pair in the database. If key already exists, then the value will be overwritten.

    Returns:
        Dict: Returns the operation status.
    """
    request_count.inc()
    data = request.get_json()
    key = data['key']
    value = data['value']
    try:
        # Set the key value pair to the database
        db.set(key, value)
        return jsonify({'message': 'key set'})

    except Exception as err:
        return jsonify({'error': err})


@app.route('/search', methods=['GET'])
def search():
    """ Search for all the keys that are present in the database with the provided prefix or suffix.

    Returns:
        Dict: List of all the keys that are starting with the prefix or ending with the suffix.
    """
    request_count.inc()
    args = request.args
    keys = []

    try:
        if 'prefix' in args:
            cache_hits.inc()

            # encode required as redis database accepts bytes as datatype
            prefix = args['prefix'].encode('utf-8')
            start_time = time.time()

            # decode required as redis database returns data in bytes
            keys = [key.decode('utf-8')
                    for key in db.keys() if key.startswith(prefix)]
            latency.observe(time.time() - start_time)


        elif 'suffix' in args:

            cache_hits.inc()

            # encode required as redis database accepts bytes as datatype
            suffix = args['suffix'].encode('utf-8')
            start_time = time.time()

            # decode required as redis database returns data in bytes
            keys = [key.decode('utf-8')
                    for key in db.keys() if key.endswith(suffix)]
            latency.observe(time.time() - start_time)

        values = [val.decode('utf-8') for val in db.mget(keys)]
        result = dict(zip(keys, values))

        return jsonify(result)
    
    except Exception as err:
        return jsonify({'error': err})


@app.route('/delete', methods=['POST'])
def delete():
    """ Deletes the key value pair from the database.

    Returns:
        Dict: Returns the status of the operation.
    """
    request_count.inc()
    data = request.get_json()
    key = data['key']
    if key in db:
        try:
            cache_hits.inc()

            start_time = time.time()
            db.delete(key)
            latency.observe(time.time() - start_time)
            return jsonify({'message': 'key deleted'})
        
        except Exception as err:
            return jsonify({'error': err})

    return jsonify({'message': 'key not found'})


@app.route('/health')
def health():
    """ Health Check endpoint to check the connection with the database.

    Returns:
        Dict: Returns metrics and status of the connection with the database.
    """
    start_time = time.time()

    try:
        # Check database connection through a simple ping
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
    """ Prometheus endpoint for metrics generation.

    Returns:
        str: Latest log and metric information of the defined application.
    """
    return generate_latest()
