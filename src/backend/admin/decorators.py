"""
Admin authorization decorators.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


def require_admin(func):
    """
    Decorator to require admin user type.
    """

    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        from backend.models import User, UserType

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.user_type != UserType.ADMIN:
            return (
                jsonify(
                    {
                        "error": "Admin access required",
                        "message": "You must be an administrator to access this resource",
                    }
                ),
                403,
            )

        return func(*args, **kwargs)

    return wrapper
