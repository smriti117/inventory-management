import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.category import Category
from schemas.category_schema import CategoryCreate
from fastapi import status
from helpers import response_parser
from config import messages

logger = logging.getLogger(__name__)


async def get_all_categories(db: Session):
    try:
        stmt = select(Category)
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as err:
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def create_category(db: Session, category_data: CategoryCreate):
    try:
        new_category = Category(**category_data.model_dump())
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        return new_category
    except Exception as err:
        await db.rollback()
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        
        # Check if it's a unique constraint violation
        if "duplicate key" in str(err) and "categories_name_key" in str(err):
            raise response_parser.generate_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Category with this name already exists",
                success=False,
            )
        
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )
