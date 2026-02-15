from fastapi import status
from sqlalchemy.orm import Session
from helpers.response_parser import generate_response
from services import product_service
from schemas.product_schema import ProductCreate, ProductUpdate


async def get_all_products_controller(
    db: Session, category_id: int = None, search: str = None
):
    products = await product_service.get_all_products(db, category_id, search)
    return generate_response(
        data=products,
        message="Products retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


async def get_product_vendors_controller(db: Session, product_id: int):
    vendors = await product_service.get_product_vendors(db, product_id)
    return generate_response(
        data=vendors,
        message="Product vendors retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


async def create_product_controller(db: Session, payload: ProductCreate, user_id: int):
    product = await product_service.create_product(db, payload, user_id)
    return generate_response(
        data=product,
        message="Product created successfully",
        status_code=status.HTTP_201_CREATED,
    )


async def get_product_controller(db: Session, product_id: int):
    product = await product_service.get_product_by_id(db, product_id)
    if not product:
        return generate_response(
            message="Product not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return generate_response(
        data=product,
        message="Product retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


async def update_product_controller(
    db: Session, product_id: int, payload: ProductUpdate, current_user
):
    try:
        product = await product_service.update_product(
            db, product_id, payload, current_user
        )
        if not product:
            return generate_response(
                message="Product not found",
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return generate_response(
            data=product,
            message="Product updated successfully",
            status_code=status.HTTP_200_OK,
        )

    except Exception as err:
        await db.rollback()
        raise err from err
