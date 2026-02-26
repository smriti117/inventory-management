from functools import wraps
from fastapi import status, HTTPException
from enums.enum_helper import UserRole


def role_required(allowed_roles: list[UserRole]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs (FastAPI dependency injection)
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
