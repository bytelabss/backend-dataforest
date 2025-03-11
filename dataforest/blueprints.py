from .users.blueprint import bp as users_bp


def init_blueprints(app):
    app.register_blueprint(users_bp)
