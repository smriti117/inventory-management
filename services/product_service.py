import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.product import Product, VendorProductMapping
from models.vendor import Vendor
from schemas.product_schema import ProductCreate, ProductUpdate
from fastapi import status
from helpers import response_parser
from config import messages

from enums.enum_helper import UserRole

logger = logging.getLogger(__name__)


async def get_all_products(db: Session, category_id: int = None, search: str = None):
    try:
        stmt = select(Product).where(Product.is_active)
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if search:
            stmt = stmt.where(
                Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%")
            )

        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as err:
        if hasattr(err, "status_code"):
            raise err
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def get_product_by_id(db: Session, product_id):
    try:
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        return result.scalars().first()
    except Exception as err:
        if hasattr(err, "status_code"):
            raise err
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def get_product_vendors(db: Session, product_id: int):
    try:
        stmt = (
            select(
                Vendor.id,
                Vendor.vendor_code,
                Vendor.company_name,
                VendorProductMapping.unit_price,
                VendorProductMapping.vendor_sku,
            )
            .join(VendorProductMapping, Vendor.id == VendorProductMapping.vendor_id)
            .where(VendorProductMapping.product_id == product_id)
        )
        result = await db.execute(stmt)
        return result.mappings().all()
    except Exception as err:
        if hasattr(err, "status_code"):
            raise err
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def create_product(db: Session, product_data: ProductCreate, user_id: int):
    try:
        new_product = Product(**product_data.model_dump(), created_by=user_id)
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return new_product
    except Exception as err:
        await db.rollback()
        if hasattr(err, "status_code"):
            raise err
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def update_product(
    db: Session, product_id: int, product_data: ProductUpdate, current_user
):
    try:
        product = await get_product_by_id(db, product_id)
        if not product:
            return None

        if (
            current_user.role == UserRole.VENDOR
            and product.created_by != current_user.id
        ):
            raise response_parser.generate_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="You can only edit products you created",
                success=False,
            )

        update_data = product_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        await db.commit()
        await db.refresh(product)
        return product
    except Exception as err:
        await db.rollback()
        if hasattr(err, "status_code"):
            raise err
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )
