from .root import bp_root
from .dashboard import bp_dashboard
from .latih import bp_latih
from .uji import bp_uji

def register_routes(app):
    app.register_blueprint(bp_root)
    app.register_blueprint(bp_dashboard)
    app.register_blueprint(bp_latih)
    app.register_blueprint(bp_uji)
