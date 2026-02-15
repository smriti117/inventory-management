import logging
from fastapi import status
from sqlalchemy.orm import Session

from config import messages
from config.settings import env
from database.security import verify_hash
from helpers.response_parser import generate_response
from helpers.token_generator import TokenGenerator
from schemas.auth_schema import Login
from services import users_service

logger = logging.getLogger(__name__)


async def login_controller(payload: Login, db: Session):
    user_exists = await users_service.get_user_by_email(db=db, user_email=payload.email)

    if not user_exists:
        raise generate_response(
            message=messages.USER_DOES_NOT_EXISTS,
            success=False,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    password_verified = verify_hash(user_exists.password_hash, payload.password)

    if not password_verified:
        raise generate_response(
            message=messages.INVALID_CREDENTIALS,
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    token = TokenGenerator.encode_token(
        user_exists, expire_time_in_mins=env.jwt_access_token_expire_minutes
    )

    return generate_response(
        message=messages.LOGIN_SUCCESS,
        success=True,
        status_code=status.HTTP_200_OK,
        data={
            "token": token,
            "username": user_exists.name,
            "user_role": user_exists.role,
        },
    )


async def get_me_details_controller(db: Session, current_user):
    details = await users_service.get_user_dashboard_details(db, current_user)
    return generate_response(
        data=details,
        message="User details retrieved successfully",
        status_code=status.HTTP_200_OK,
    )
