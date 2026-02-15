from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category_id: int
    measurement_unit: str
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    measurement_unit: Optional[str] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    created_by: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductListRes(BaseModel):
    payload: List[Product]
    model_config = ConfigDict(from_attributes=True)


class ProductRes(BaseModel):
    payload: Product
    model_config = ConfigDict(from_attributes=True)
