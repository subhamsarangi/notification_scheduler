import os
import logging

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

encryption_key = os.environ.get("ENCRYPTION_KEY")
if encryption_key is None:
    raise ValueError(
        "--------Encryption key not found in environment variables.-------"
    )
fernet = Fernet(encryption_key)


def create_app():
    from models import db
    from routes import api
    from config import Config

    app = Flask(__name__)
    app.debug = True

    # Load the configuration
    app.config.from_object(Config)

    # Enable CORS for all routes and allow requests from localhost:5000
    CORS(
        app,
        resources={r"/*": {"origins": ["http://127.0.0.1:5500"]}},
    )

    db.init_app(app)
    
    logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    app.register_blueprint(api, url_prefix="/api")

    DebugToolbarExtension(app)

    with app.app_context():
        db.create_all()

    os.makedirs("files", exist_ok=True)
    with open("files/sample.txt", "w") as f:
        f.write("This is a test file.")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
