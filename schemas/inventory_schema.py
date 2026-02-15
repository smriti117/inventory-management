from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from enums.enum_helper import InventoryTransactionType


class InventoryTransactionBase(BaseModel):
    product_id: int
    transaction_type: InventoryTransactionType
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    quantity_change: int


class InventoryTransaction(InventoryTransactionBase):
    id: int
    quantity_before: int
    quantity_after: int
    created_by: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StockBase(BaseModel):
    product_id: int
    current_quantity: int = 0
    reorder_level: int = 0


class Stock(StockBase):
    id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StockRes(BaseModel):
    payload: Stock
    model_config = ConfigDict(from_attributes=True)


class StockListRes(BaseModel):
    payload: List[Stock]
    model_config = ConfigDict(from_attributes=True)
