from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    status_code: int = 200
    message: Optional[str] = ""
    data: Optional[T] = None
    success: bool = True

    class Config:
        from_attributes = True
