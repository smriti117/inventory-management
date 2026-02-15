from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal


class VendorProductMappingBase(BaseModel):
    vendor_id: int
    product_id: int
    vendor_sku: Optional[str] = None
    min_order_quantity: Optional[int] = 1
    unit_price: Decimal
    days_to_delivery: Optional[int] = 0
    is_preferred: bool = False


class VendorProductMappingCreate(VendorProductMappingBase):
    pass


class VendorProductMappingUpdate(BaseModel):
    vendor_sku: Optional[str] = None
    min_order_quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    days_to_delivery: Optional[int] = None
    is_preferred: Optional[bool] = None


class VendorProductMapping(VendorProductMappingBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class VendorProductMappingRes(BaseModel):
    payload: VendorProductMapping
    model_config = ConfigDict(from_attributes=True)


class VendorProductMappingListRes(BaseModel):
    payload: List[VendorProductMapping]
    model_config = ConfigDict(from_attributes=True)


class ProductInVendor(BaseModel):
    id: int
    sku: str
    name: str
    unit_price: Decimal
    vendor_sku: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class VendorProductListRes(BaseModel):
    payload: List[ProductInVendor]
    model_config = ConfigDict(from_attributes=True)
