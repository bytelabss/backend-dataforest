from .auth.blueprints import bp as auth_bp
from .users.blueprints import bp as users_bp
from .reforested_area.blueprints import bp as reflorested_area_bp
from .termo_consentimento.blueprints import bp as consent
from .models.blueprints import bp as models
from .geospatial_data.blueprints import bp as geospatial_data_bp

def init_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(reflorested_area_bp)
    app.register_blueprint(consent)
    app.register_blueprint(models)
    app.register_blueprint(geospatial_data_bp)