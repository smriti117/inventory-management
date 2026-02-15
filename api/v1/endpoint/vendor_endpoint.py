from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database.engine import get_db
from helpers.token_generator import TokenGenerator
from api.v1.controller import vendor_controller
from schemas.vendor_schema import VendorCreate, VendorUpdate
from schemas.mapping_schema import VendorProductMappingCreate
from enums.enum_helper import UserRole
from helpers.rbac_helper import role_required

vendor_router = APIRouter(prefix="/vendor")


@vendor_router.get("/", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN])
async def get_vendors(
    db: Session = Depends(get_db), current_user=Depends(TokenGenerator.decode_token)
):
    return await vendor_controller.get_all_vendors_controller(db)


@vendor_router.post("/", status_code=status.HTTP_201_CREATED)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN])
async def create_vendor(
    payload: VendorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await vendor_controller.create_vendor_controller(db, payload)


@vendor_router.get("/{vendor_id}", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN])
async def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await vendor_controller.get_vendor_controller(db, vendor_id)


@vendor_router.get("/{vendor_id}/products", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN, UserRole.VENDOR])
async def get_vendor_products(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await vendor_controller.get_vendor_products_controller(db, vendor_id)


@vendor_router.post("/product-mapping", status_code=status.HTTP_201_CREATED)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN, UserRole.VENDOR])
async def create_mapping(
    payload: VendorProductMappingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await vendor_controller.create_vendor_product_mapping_controller(db, payload)
