from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class VendorLocationBase(BaseModel):
    address_line1: str
    city: str
    state: str
    country: str
    postal_code: str
    is_primary: bool = False


class VendorLocationCreate(VendorLocationBase):
    pass


class VendorLocation(VendorLocationBase):
    id: int
    vendor_id: int
    model_config = ConfigDict(from_attributes=True)


class VendorBase(BaseModel):
    vendor_code: str
    company_name: str
    is_active: bool = True


class VendorCreate(BaseModel):
    company_name: str
    is_active: bool = True
    locations: List[VendorLocationCreate] = []


class VendorUpdate(BaseModel):
    company_name: Optional[str] = None
    is_active: Optional[bool] = None


class Vendor(VendorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    locations: List[VendorLocation] = []

    model_config = ConfigDict(from_attributes=True)


class VendorListRes(BaseModel):
    payload: List[Vendor]
    model_config = ConfigDict(from_attributes=True)


class VendorRes(BaseModel):
    payload: Vendor
    model_config = ConfigDict(from_attributes=True)
