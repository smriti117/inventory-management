from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CategoryListRes(BaseModel):
    payload: List[Category]
    model_config = ConfigDict(from_attributes=True)
