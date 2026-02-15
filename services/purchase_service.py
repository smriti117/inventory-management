import logging
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models.purchase import PurchaseOrder, PurchaseOrderItem
from models.product import VendorProductMapping
from schemas.purchase_schema import PurchaseOrderCreate
from services import inventory_service
from enums.enum_helper import PurchaseOrderStatus, InventoryTransactionType
from fastapi import status
from helpers import response_parser
from config import messages

logger = logging.getLogger(__name__)


async def get_all_purchase_orders(db: Session):
    try:
        stmt = select(PurchaseOrder)
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as err:
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def create_purchase_order(
    db: Session, po_data: PurchaseOrderCreate, user_id: int
):
    try:
        for item in po_data.items:
            mapping_stmt = select(VendorProductMapping).where(
                VendorProductMapping.product_id == item.product_id,
                VendorProductMapping.vendor_id == po_data.vendor_id,
            )
            mapping_res = await db.execute(mapping_stmt)
            if not mapping_res.scalars().first():
                raise response_parser.generate_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=f"Vendor is not linked to product {item.product_id}",
                    success=False,
                )

        count_stmt = select(func.count(PurchaseOrder.id))
        count_res = await db.execute(count_stmt)
        count = count_res.scalar()
        po_number = f"PO-{(count + 1):06d}"

        total_amount = sum(item.quantity * item.unit_price for item in po_data.items)

        new_po = PurchaseOrder(
            po_number=po_number,
            vendor_id=po_data.vendor_id,
            status=PurchaseOrderStatus.DRAFT,
            total_amount=total_amount,
            notes=po_data.notes,
            created_by=user_id,
        )
        db.add(new_po)
        await db.flush()

        for item in po_data.items:
            new_item = PurchaseOrderItem(
                purchase_order_id=new_po.id,
                product_id=item.product_id,
                ordered_quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price,
            )
            db.add(new_item)

        await db.commit()
        await db.refresh(new_po)
        return new_po
    except Exception as err:
        if isinstance(err, Exception) and hasattr(err, "status_code"):
            raise err
        await db.rollback()
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )


async def update_po_status(db: Session, po_id: int, new_status: PurchaseOrderStatus):
    try:
        stmt = select(PurchaseOrder).where(PurchaseOrder.id == po_id)
        result = await db.execute(stmt)
        po = result.scalars().first()
        if not po:
            return None

        po.status = new_status
        await db.flush()

        if new_status == PurchaseOrderStatus.RECEIVED:
            stmt_items = select(PurchaseOrderItem).where(
                PurchaseOrderItem.purchase_order_id == po.id
            )
            items_res = await db.execute(stmt_items)
            items = items_res.scalars().all()

            for item in items:
                await inventory_service.update_stock(
                    db=db,
                    product_id=item.product_id,
                    quantity_change=item.ordered_quantity,
                    transaction_type=InventoryTransactionType.INBOUND,
                    user_id=po.created_by,
                    reference_id=po.id,
                    reference_type="purchase_order",
                )

        await db.commit()
        await db.refresh(po)
        return po
    except Exception as err:
        await db.rollback()
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )
