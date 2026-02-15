from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database.engine import get_db
from api.v1.controller import inventory_controller
from enums.enum_helper import UserRole
from helpers.rbac_helper import role_required
from helpers.token_generator import TokenGenerator

inventory_router = APIRouter(prefix="/inventory")


@inventory_router.get("/stock", status_code=status.HTTP_200_OK)
@role_required(allowed_roles=[UserRole.SUPER_ADMIN, UserRole.VENDOR, UserRole.CUSTOMER])
async def get_stocks(
    db: Session = Depends(get_db),
    current_user=Depends(TokenGenerator.decode_token),
):
    return await inventory_controller.get_all_stocks_controller(db)
