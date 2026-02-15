from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database.engine import get_db
from helpers.token_generator import TokenGenerator
from api.v1.controller import purchase_controller
from schemas.purchase_schema import PurchaseOrderCreate
from enums.enum_helper import PurchaseOrderStatus, UserRole
from helpers.rbac_helper import role_required

purchase_router = APIRouter(prefix="/purchase-order")


@purchase_router.get("/", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN])
async def get_purchase_orders(
    db: Session = Depends(get_db), current_user=Depends(TokenGenerator.decode_token)
):
    return await purchase_controller.get_all_pos_controller(db)


@purchase_router.post("/", status_code=status.HTTP_201_CREATED)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN])
async def create_purchase_order(
    payload: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await purchase_controller.create_po_controller(db, payload, current_user.id)


@purchase_router.patch("/{po_id}/status", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN])
async def update_po_status(
    po_id: int,
    new_status: PurchaseOrderStatus,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await purchase_controller.update_po_status_controller(db, po_id, new_status)
