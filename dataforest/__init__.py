from flask import Flask, send_from_directory
from flask_cors import CORS

from .config import Config
from .log import init_log
from .database import init_db_from_schema, load_models
from .blueprints import init_blueprints


def create_app(config=Config):
    init_log(config)

    try:
        config.validate_settings()
    except ValueError as e:
        print(f"Invalid configuration! {e}")
        exit(1)

    app = Flask(__name__)

    if __name__ == "main":
        app.run(debug=False)

    app.config.from_object(config)
    app.json.sort_keys = Config.JSON_SORT_KEYS

    CORS(app)

    load_models()

    init_blueprints(app)

    with app.app_context():
        init_db_from_schema()

    @app.get("/")
    def index():
        return {"message": "Welcome to the Data Forest REST API"}

    @app.get("/apispec")
    def apispec():
        return send_from_directory(Config.STATIC_DIR, "swagger.yml")

    @app.get("/docs")
    def apidocs():
        return send_from_directory(Config.STATIC_DIR, "swagger.html")

    return app
