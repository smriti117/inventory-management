import logging

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from schemas import api_response

logger = logging.getLogger(__name__)


def generate_response(
    status_code=status.HTTP_200_OK,
    message="",
    data=[],
    success=True,
    media_type="application/json",
    headers={},
):
    try:
        if status_code not in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_202_ACCEPTED,
            status.HTTP_204_NO_CONTENT,
        ]:
            return HTTPException(
                status_code=status_code,
                detail=jsonable_encoder(
                    api_response.APIResponse(
                        status_code=status_code,
                        message=str(message),
                        data=data,
                        success=success,
                    ).model_dump()
                ),
            )
        else:
            return JSONResponse(
                status_code=status_code,
                media_type=media_type,
                headers=headers,
                content=jsonable_encoder(
                    api_response.APIResponse(
                        status_code=status_code,
                        message=str(message),
                        data=data,
                        success=success,
                    ).model_dump()
                ),
            )
    except Exception as err:
        logger.error(f"Error Occurred in generate_response() {err}")
