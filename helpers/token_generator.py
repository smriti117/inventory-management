import logging
from datetime import datetime, timedelta, timezone

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session

from config.settings import env
from database.engine import get_db
from helpers import response_parser
from schemas.users_schema import Users
from services import users_service

logger = logging.getLogger(__name__)
security = HTTPBearer()


class TokenGenerator:
    @staticmethod
    def encode_token(user_exists: Users, expire_time_in_mins: int, data: dict = None):
        """
        The encode_token function takes in a user object and returns a token
        """
        logger.info("encode_token function is executing")
        try:
            payload = {
                "exp": datetime.now(timezone.utc)
                + timedelta(minutes=expire_time_in_mins),
                "sub": str(user_exists.id),
                "data": data,
            }

            token = jwt.encode(payload, env.jwt_secret_key, algorithm=env.jwt_algorithm)

            return token

        except Exception as err:
            logger.error("Error occurred in Token Generation %s", err, exc_info=True)
            raise response_parser.generate_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unable to encode data",
                success=False,
            )

    @staticmethod
    async def decode_token(
        auth: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
    ):
        """
        It takes a token, decodes it, and returns the decoded token
        """
        try:
            token = auth.credentials
            token = auth.credentials

            credentials_exception = response_parser.generate_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Could not validate credentials",
                success=False,
            )

            payload = jwt.decode(
                token, env.jwt_secret_key, algorithms=[env.jwt_algorithm]
            )

            user_id = payload.get("sub")

            if user_id is None:
                raise credentials_exception

            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id in token sub claim: {user_id}")
                raise credentials_exception

        except ExpiredSignatureError:
            raise response_parser.generate_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Token expired",
                success=False,
            )

        except JWTError as err:
            logger.error("Error occurred in token decoding %s", err, exc_info=True)
            raise credentials_exception

        user = await users_service.get_user_by_id(db=db, user_id=user_id)

        if user is None:
            raise credentials_exception

        return user
