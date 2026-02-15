from fastapi import status
from sqlalchemy.orm import Session
from helpers.response_parser import generate_response
from services import inventory_service


async def get_all_stocks_controller(db: Session):
    stocks = await inventory_service.get_all_stocks(db)
    return generate_response(
        data=stocks,
        message="Inventory stocks retrieved successfully",
        status_code=status.HTTP_200_OK,
    )
