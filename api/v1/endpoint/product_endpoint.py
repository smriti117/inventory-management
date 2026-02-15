from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from database.engine import get_db
from helpers.token_generator import TokenGenerator
from api.v1.controller import product_controller
from schemas.product_schema import ProductCreate, ProductUpdate
from enums.enum_helper import UserRole
from helpers.rbac_helper import role_required
from typing import Optional

product_router = APIRouter(prefix="/product")


@product_router.get("/", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN, UserRole.VENDOR, UserRole.CUSTOMER])
async def get_products(
    db: Session = Depends(get_db),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await product_controller.get_all_products_controller(db, category_id, search)


@product_router.get("/{product_id}/vendors", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN, UserRole.VENDOR, UserRole.CUSTOMER])
async def get_product_vendors(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await product_controller.get_product_vendors_controller(db, product_id)


@product_router.get("/{product_id}", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN, UserRole.VENDOR, UserRole.CUSTOMER])
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await product_controller.get_product_controller(db, product_id)


@product_router.post("/", status_code=status.HTTP_201_CREATED)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN, UserRole.VENDOR])
async def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await product_controller.create_product_controller(
        db, payload, current_user.id
    )


@product_router.put("/{product_id}", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN, UserRole.VENDOR])
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await product_controller.update_product_controller(
        db, product_id, payload, current_user
    )
