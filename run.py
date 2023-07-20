import os
from waitress import serve
from dotenv import load_dotenv
from app.kvstore_app import app, start_prometheus_server

load_dotenv()

flask_host = os.getenv("HOST")
flask_port = os.getenv("PORT")

if __name__ == "__main__":
    start_prometheus_server()
    serve(app=app, host=flask_host, port=flask_port)
