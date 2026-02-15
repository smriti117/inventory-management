from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from enums.enum_helper import PurchaseOrderStatus


class PurchaseOrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass


class PurchaseOrderItem(PurchaseOrderItemBase):
    id: int
    purchase_order_id: int
    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderBase(BaseModel):
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    vendor_id: int
    items: List[PurchaseOrderItemCreate]


class PurchaseOrder(PurchaseOrderBase):
    id: int
    po_number: str
    status: PurchaseOrderStatus
    total_amount: Decimal
    created_by: int
    created_at: datetime
    items: List[PurchaseOrderItem] = []

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderListRes(BaseModel):
    payload: List[PurchaseOrder]
    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderRes(BaseModel):
    payload: PurchaseOrder
    model_config = ConfigDict(from_attributes=True)
