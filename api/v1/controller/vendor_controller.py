import logging
from fastapi import status
from sqlalchemy.orm import Session
from helpers.response_parser import generate_response
from services import vendor_service
from schemas.vendor_schema import VendorCreate
from schemas.mapping_schema import VendorProductMappingCreate

logger = logging.getLogger(__name__)


async def get_all_vendors_controller(db: Session):
    vendors = await vendor_service.get_all_vendors(db)
    return generate_response(
        data=vendors,
        message="Vendors retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


async def create_vendor_controller(db: Session, payload: VendorCreate):
    vendor = await vendor_service.create_vendor(db, payload)
    return generate_response(
        data=vendor,
        message="Vendor created successfully",
        status_code=status.HTTP_201_CREATED,
    )


async def get_vendor_controller(db: Session, vendor_id):
    vendor = await vendor_service.get_vendor_by_id(db, vendor_id)
    if not vendor:
        return generate_response(
            message="Vendor not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return generate_response(
        data=vendor,
        message="Vendor retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


async def get_vendor_products_controller(db: Session, vendor_id):
    products = await vendor_service.get_vendor_products(db, vendor_id)
    return generate_response(
        data=products,
        message="Vendor products retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


async def create_vendor_product_mapping_controller(
    db: Session, payload: VendorProductMappingCreate
):
    mapping = await vendor_service.create_vendor_product_mapping(db, payload)
    return generate_response(
        data=mapping,
        message="Product linked to vendor successfully",
        status_code=status.HTTP_201_CREATED,
    )
