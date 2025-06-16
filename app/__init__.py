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

    print("🔑 SECRET_KEY =", app.config['SECRET_KEY'])

    @app.before_request
    def log_session():
        print("[Session Check]", dict(session))

    def restrict_access():
        from flask import request, redirect, url_for, flash
        public_endpoints = ['login.login', 'register.register', 'static']

        if not session.get('user_id') and request.endpoint not in public_endpoints:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for('login.login'))

        if session.get('user_id') and request.endpoint in ['login.login', 'register.register']:
            return redirect(url_for('dashboard.index'))

    @app.after_request
    def log_after_request(response):
        print("[After Request] session:", dict(session))
        return response

    return app
