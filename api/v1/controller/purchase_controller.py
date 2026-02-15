from fastapi import status
from sqlalchemy.orm import Session
from helpers.response_parser import generate_response
from services import purchase_service
from schemas.purchase_schema import PurchaseOrderCreate
from enums.enum_helper import PurchaseOrderStatus


async def get_all_pos_controller(db: Session):
    pos = await purchase_service.get_all_purchase_orders(db)
    return generate_response(
        data=pos,
        message="Purchase orders retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


async def create_po_controller(db: Session, payload: PurchaseOrderCreate, user_id: int):
    po = await purchase_service.create_purchase_order(db, payload, user_id)
    return generate_response(
        data=po,
        message="Purchase order created successfully",
        status_code=status.HTTP_201_CREATED,
    )


async def update_po_status_controller(
    db: Session, po_id: int, new_status: PurchaseOrderStatus
):
    po = await purchase_service.update_po_status(db, po_id, new_status)
    if not po:
        return generate_response(
            message="Purchase order not found",
            success=False,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return generate_response(
        data=po,
        message=f"Purchase order status updated to {new_status}",
        status_code=status.HTTP_200_OK,
    )
