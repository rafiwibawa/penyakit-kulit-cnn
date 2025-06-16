from .root import bp_root
from .dashboard import bp_dashboard
from .latih import bp_latih
from .uji import bp_uji
from .login import bp_login
from .register import bp_register
from .diagnoses import bp_diagnoses

def register_routes(app):
    app.register_blueprint(bp_root)
    app.register_blueprint(bp_dashboard)
    app.register_blueprint(bp_latih)
    app.register_blueprint(bp_uji)
    app.register_blueprint(bp_login)
    app.register_blueprint(bp_register)
    app.register_blueprint(bp_diagnoses)
