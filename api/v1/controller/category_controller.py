from fastapi import status
from sqlalchemy.orm import Session
from helpers.response_parser import generate_response
from services import category_service
from schemas.category_schema import CategoryCreate


async def get_all_categories_controller(db: Session):
    categories = await category_service.get_all_categories(db)
    return generate_response(
        data=categories,
        message="Categories retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


async def create_category_controller(db: Session, payload: CategoryCreate):
    category = await category_service.create_category(db, payload)
    return generate_response(
        data=category,
        message="Category created successfully",
        status_code=status.HTTP_201_CREATED,
    )
