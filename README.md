This project implements a simple key-value store API service with in-memory storage. 

## Features

- In-memory storage using Redis
- REST API with JSON responses  
- CRUD operations for key-value pairs
- Search/filter keys by prefix or suffix
- Containerized with Docker 
- Kubernetes deployment configuration
- CI/CD pipelines for testing and deployment

## Usage

### Local Development

#### Prerequisites

- Python 3.7+ 
- Pip
- Redis

#### Setup

```bash
# Clone repo
git clone https://github.com/shiraguppipavan/kvstore.git

# Install dependencies
pip install -r requirements.txt

# Start Redis
redis-server

# Run server
python run.py
```

The API will be running at http://localhost:5000

### Docker

A Dockerfile is provided to build an image for the API app.

```
docker build -t kvstore .
docker run -p 5000:5000 kvstore
```

Redis also needs to be running in a separate container or on the host.

### Kubernetes

Kubernetes manifests are in the `k8s` directory for deploying to a Kubernetes cluster.

Includes StatefulSet, Service and Ingress.

```
kubectl apply -f k8s/
```

### Endpoints

- `GET /get/<key>` - Get value for given key
- `POST /set` - Set key-value pair (JSON body)
- `GET /search?prefix=<prefix>&suffix=<suffix>` - Search keys by prefix and/or suffix
- `GET /delete` - Delete value for the given key (JSON body)
- `GET /health` - Healthcheck endpoint


## Development

### Code Structure

- `app.py` - Main Flask app 
- `tests.py` - Test app
- `run.py` - Run Flask app

### Running Tests

Run with:

```
pytest 
```

### Environment Variables

- `FLASK_ENV` - Environment mode (development/production)
- `PORT` - Port for app to run on
- `REDIS_HOST` - Redis host 
- `REDIS_PORT` - Redis port

## Deployment

The main branches are:

- `master` - Main production branch
- `develop` - Development branch for testing new features
- Feature branches used for specific features/fixes

## Monitoring & Logging

The app uses the following tools for observability:

- Prometheus - Metrics collection
- Grafana - Visualize metrics
- ELK - Log aggregation with Elasticsearch, Logstash and Kibana
