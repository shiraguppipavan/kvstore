import os
from waitress import serve
from dotenv import load_dotenv
from app.kvstore_app import app

load_dotenv()

flask_host = os.getenv("HOST")
flask_port = os.getenv("PORT")

if __name__ == "__main__":
    serve(app=app, host=flask_host, port=flask_port)
