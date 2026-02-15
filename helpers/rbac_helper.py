from functools import wraps
from fastapi import status
from helpers.response_parser import generate_response
from enums.enum_helper import UserRole


def role_required(allowed_roles: list[UserRole]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            current_user = kwargs.get("current_user")

            if not current_user:
                return generate_response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message="Authentication required",
                    success=False,
                )

            if current_user.role not in allowed_roles:
                return generate_response(
                    status_code=status.HTTP_403_FORBIDDEN,
                    message="You do not have permission to perform this action",
                    success=False,
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
