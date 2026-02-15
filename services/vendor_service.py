import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.vendor import Vendor, VendorLocation
from models.product import VendorProductMapping, Product
from schemas.vendor_schema import VendorCreate, VendorUpdate
from schemas.mapping_schema import VendorProductMappingCreate
from fastapi import status
from helpers import response_parser
from config import messages

logger = logging.getLogger(__name__)


async def get_all_vendors(db: Session):
    try:
        stmt = select(Vendor).where(Vendor.is_active)
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as err:
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def get_vendor_by_id(db: Session, vendor_id):
    try:
        stmt = select(Vendor).where(Vendor.id == vendor_id)
        result = await db.execute(stmt)
        return result.scalars().first()
    except Exception as err:
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def create_vendor(db: Session, vendor_data: VendorCreate):
    try:
        count_stmt = select(Vendor.id)
        result = await db.execute(count_stmt)
        count = len(result.scalars().all())
        vendor_code = f"VND-{(count + 1):04d}"

        new_vendor = Vendor(
            vendor_code=vendor_code,
            company_name=vendor_data.company_name,
            is_active=vendor_data.is_active,
        )
        db.add(new_vendor)
        await db.flush()

        for loc in vendor_data.locations:
            new_loc = VendorLocation(vendor_id=new_vendor.id, **loc.model_dump())
            db.add(new_loc)

        await db.commit()
        await db.refresh(new_vendor)
        return new_vendor
    except Exception as err:
        await db.rollback()
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def update_vendor(db: Session, vendor_id, vendor_data: VendorUpdate):
    try:
        vendor = await get_vendor_by_id(db, vendor_id)
        if not vendor:
            return None

        if vendor_data.company_name is not None:
            vendor.company_name = vendor_data.company_name
        if vendor_data.is_active is not None:
            vendor.is_active = vendor_data.is_active

        await db.commit()
        await db.refresh(vendor)
        return vendor
    except Exception as err:
        await db.rollback()
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def get_vendor_products(db: Session, vendor_id: int):
    try:
        stmt = (
            select(
                Product.id,
                Product.sku,
                Product.name,
                VendorProductMapping.unit_price,
                VendorProductMapping.vendor_sku,
            )
            .join(VendorProductMapping, Product.id == VendorProductMapping.product_id)
            .where(VendorProductMapping.vendor_id == vendor_id)
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


async def create_vendor_product_mapping(
    db: Session, mapping_data: VendorProductMappingCreate
):
    try:
        # Validation for positive IDs
        if mapping_data.vendor_id <= 0 or mapping_data.product_id <= 0:
            raise response_parser.generate_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Vendor ID and Product ID must be positive integers",
                success=False,
            )

        stmt = select(VendorProductMapping).where(
            VendorProductMapping.vendor_id == mapping_data.vendor_id,
            VendorProductMapping.product_id == mapping_data.product_id,
        )
        result = await db.execute(stmt)
        existing_mapping = result.scalars().first()

        if existing_mapping:
            raise response_parser.generate_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Mapping already exists between this vendor and product",
                success=False,
            )

        new_mapping = VendorProductMapping(**mapping_data.model_dump())
        db.add(new_mapping)
        await db.commit()
        await db.refresh(new_mapping)
        return new_mapping
    except Exception as err:
        if hasattr(err, "status_code"):
            raise err
        await db.rollback()
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )
