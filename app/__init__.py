import os
from flask import Flask
from flask_smorest import Api

from app.config import Config, TestConfig
from app.extensions import db, jwt, ma

MODE = os.getenv("FLASK_ENV", "development")


def create_app(config_class=Config):
    app = Flask(__name__)

    if MODE == "testing":
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(config_class)

    app.config["API_SPEC_OPTIONS"] = {
        "security": [{"bearerAuth": []}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
    }

    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    from app.routes import bp as api_blueprint

    api = Api(app)
    api.register_blueprint(api_blueprint)

    with app.app_context():
        db.create_all()

    return app
