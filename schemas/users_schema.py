import re

from marshmallow import Schema, ValidationError, fields, validates
from pydantic import BaseModel, EmailStr
from typing import List
from schemas.product_schema import Product
from schemas.mapping_schema import VendorProductMapping


class Users(BaseModel):
    id: int | None = None
    name: str | None = None
    email: EmailStr | None = None
    # password: str | None = None
    # salt: str
    mobile: str | None = None
    # role: RoleMaster | None = None

    class Config:
        from_attributes = True


class UsersRes(BaseModel):
    payload: Users

    class Config:
        from_attributes = True


class UsersCreate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    mobile: str | None = None
    role_id: int | None = None

    class Config:
        from_attributes = True


class UsersCreateMarsh(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    mobile = fields.Str(required=True)
    role_id = fields.Integer(required=True)

    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters")

        if not re.search(r"[A-Z]", value):
            raise ValidationError("Password must include at least one capital letter")

        if not re.search(r"[0-9]", value):
            raise ValidationError("Password must include at least one number")

        if not re.search(r"[!@#$%^&*()\-_=+{};:,<.>]", value):
            raise ValidationError(
                "Password must include at least one special character"
            )

    @validates("mobile")
    def validate_mobile_number(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValidationError("Mobile number must be exactly 10 digits.")


class UsersListSchema(BaseModel):
    id: int
    user_name: str
    email: EmailStr
    mobile: str
    role: str
    created_by: str
    modified_by: str
    is_active: int
    # module_name: str
    # permission_name: str

    class Config:
        from_attributes = True


class UsersDetailSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    role_id: int
    created_by: int
    modified_by: int
    is_active: int

    class Config:
        from_attributes = True


class UsersListSchemaRes(BaseModel):
    payload: list[UsersListSchema]

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_products: int | None = None
    my_products: List[Product] = []
    total_mappings: int | None = None
    my_mappings: List[VendorProductMapping] = []
    total_users: int | None = None
    all_products: List[Product] = []
    all_mappings: List[VendorProductMapping] = []


class UserDetails(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    stats: DashboardStats


class UserDetailsRes(BaseModel):
    payload: UserDetails
