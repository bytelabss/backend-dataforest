from .users.blueprints import bp as users_bp
from .reforested_area.blueprints import bp as reflorested_area_bp


def init_blueprints(app):
    app.register_blueprint(users_bp)
    app.register_blueprint(reflorested_area_bp)
