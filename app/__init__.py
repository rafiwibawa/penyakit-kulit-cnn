from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask import session

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models
    from app.routes import register_routes
    register_routes(app)

    # 👇 Logging session
    @app.before_request
    def log_before_request():
        print("[Before Request] session:", dict(session))

    @app.after_request
    def log_after_request(response):
        print("[After Request] session:", dict(session))
        return response

    return app
