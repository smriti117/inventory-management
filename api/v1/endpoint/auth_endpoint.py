import logging

from fastapi import APIRouter, Depends, status
from marshmallow import ValidationError
from sqlalchemy.orm import Session

from api.v1.controller import auth_controller
from config import messages
from database.engine import get_db
from helpers.response_parser import generate_response
from schemas.api_response import APIResponse
from schemas.auth_schema import Login, LoginResponse
from helpers.token_generator import TokenGenerator
from schemas.users_schema import UserDetailsRes

logger = logging.getLogger(__name__)
auth_router = APIRouter(prefix="/auth")


@auth_router.post("/login", response_model=APIResponse[LoginResponse])
async def login(payload: Login, db: Session = Depends(get_db)):
    try:
        return await auth_controller.login_controller(payload=payload, db=db)

    except ValidationError as err:
        raise generate_response(
            message=messages.VALIDATION_ERROR,
            data=err.messages,
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
        )

    except Exception as err:
        logger.error("Error in login: %s", err, exc_info=True)
        if hasattr(err, "status_code"):
            raise err
        else:
            raise generate_response(
                message=messages.SOME_ERROR_OCCURRED,
                success=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@auth_router.get("/me/details", response_model=APIResponse[UserDetailsRes])
async def get_user_details(
    db: Session = Depends(get_db), current_user=Depends(TokenGenerator.decode_token)
):
    return await auth_controller.get_me_details_controller(db, current_user)
