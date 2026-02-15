import logging
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models.inventory import Stock, InventoryTransaction
from models.product import Product
from enums.enum_helper import InventoryTransactionType
from fastapi import status
from helpers import response_parser
from config import messages

logger = logging.getLogger(__name__)


async def get_all_stocks(db: Session):
    try:
        stmt = (
            select(
                Product.id.label("product_id"),
                func.coalesce(Stock.current_quantity, 0).label("current_quantity"),
                Stock.updated_at,
                Stock.id,
                func.coalesce(Stock.reorder_level, 0).label("reorder_level"),
            )
            .select_from(Product)
            .outerjoin(Stock, Product.id == Stock.product_id)
        )

        result = await db.execute(stmt)
        return result.mappings().all()
    except Exception as err:
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def update_stock(
    db: Session,
    product_id: int,
    quantity_change: int,
    transaction_type: InventoryTransactionType,
    user_id: int,
    reference_id: int = None,
    reference_type: str = None,
):
    try:
        stmt = select(Stock).where(Stock.product_id == product_id)
        result = await db.execute(stmt)
        stock = result.scalars().first()

        if not stock:
            stock = Stock(product_id=product_id, current_quantity=0)
            db.add(stock)
            await db.flush()

        quantity_before = stock.current_quantity
        stock.current_quantity += quantity_change
        quantity_after = stock.current_quantity

        transaction = InventoryTransaction(
            product_id=product_id,
            transaction_type=transaction_type,
            reference_id=reference_id,
            reference_type=reference_type,
            quantity_change=quantity_change,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            created_by=user_id,
        )
        db.add(transaction)

        return stock
    except Exception as err:
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )
