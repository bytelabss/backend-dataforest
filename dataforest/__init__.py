import json
from flask import Flask, send_from_directory
from flask_cors import CORS

from .config import Config
from .log import init_log
from .database import load_models, Session, SecondarySession
from .blueprints import init_blueprints
from .redis_client import redis_client
from .users.services import UserService
from .users_keys.services import UsersKeysService
from cryptography.fernet import Fernet



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

        usersRedis = [] 

        session = Session() 
        service = UserService(session)

        session2 = SecondarySession()
        service2 = UsersKeysService(session2)

        usuarios = service.list_users_criptografados()

        for usuario in usuarios:
            chaveDescriptografia = service2.get_user_by_user_id(usuario.id)

            if chaveDescriptografia != None:

                fernet = Fernet(chaveDescriptografia.encryption_key)

                emailDescriptografado = fernet.decrypt(usuario.email.encode("utf-8")).decode()
                full_name = fernet.decrypt(usuario.full_name.encode("utf-8")).decode()

                user_data = {
                    'id' : str(usuario.id),
                    'full_name': full_name,
                    'email': emailDescriptografado,
                }

                usersRedis.append(user_data)

        redis_client.set("users", json.dumps(usersRedis))

        session.close()

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
