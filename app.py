from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from models import db
from routes import api


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config["SECRET_KEY"] = "opensecret"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notifications.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_RECORD_QUERIES"] = True

    db.init_app(app)
    app.register_blueprint(api, url_prefix="/api")

    DebugToolbarExtension(app)
    app.config["DEBUG_TB_PROFILER_ENABLED"] = True
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
