from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv

from models import db
from routes import api
from config import Config

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.debug = True

    # Load the configuration
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(api, url_prefix="/api")

    DebugToolbarExtension(app)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
