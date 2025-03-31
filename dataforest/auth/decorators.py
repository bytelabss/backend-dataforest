from functools import wraps

from flask import request, g

from ..database import Session
from ..users.services import UserService
from .services import TokenService


def requires_auth(required_role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization", "").removeprefix("Bearer ")
            if token:
                string_token = token.encode("ascii", "ignore")
                session = Session()
                user_service = UserService(session)
                token_service = TokenService(user_service)
                user = token_service.verify_token(string_token)

                if user:
                    g.current_user = user

                    if required_role and user.role != required_role:
                        return {"message": "You do not have the required role for this action."}, 403

                    return f(*args, **kwargs)

            return {"message": "Authentication is required to access this resource"}, 401

        return decorated
    return decorator
