from typing import Optional

from marshmallow import Schema, fields, validate
from pydantic import BaseModel, EmailStr, ValidationInfo, field_validator


class LoginResponse(BaseModel):
    token: str
    username: str
    user_role_id: int
    user_role: str


class Login(BaseModel):
    email: Optional[str]
    password: Optional[str]

    class Config:
        from_attributes = True
