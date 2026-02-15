from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database.engine import get_db
from api.v1.controller import category_controller
from schemas.category_schema import CategoryCreate
from enums.enum_helper import UserRole
from helpers.rbac_helper import role_required
from helpers.token_generator import TokenGenerator

category_router = APIRouter(prefix="/category")


@category_router.get("/", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN, UserRole.VENDOR, UserRole.CUSTOMER])
async def get_categories(
    db: Session = Depends(get_db), current_user=Depends(TokenGenerator.decode_token)
):
    return await category_controller.get_all_categories_controller(db)


@category_router.post("/", status_code=status.HTTP_201_CREATED)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN])
async def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await category_controller.create_category_controller(db, payload)
