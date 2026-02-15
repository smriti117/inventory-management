import logging

from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import messages
from helpers import response_parser
from models.users import Users
from models.product import Product, VendorProductMapping
from schemas.users_schema import (
    UserDetails,
    DashboardStats,
)
from enums.enum_helper import UserRole
from sqlalchemy import func

logger = logging.getLogger(__name__)


async def get_user_by_id(db: Session, user_id):
    try:
        stmt = select(Users).where(Users.id == user_id, Users.is_active)
        result = await db.execute(stmt)
        return result.scalars().first()

    except Exception as err:
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err, exc_info=True)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"{messages.INTERNAL_SERVER_ERROR}",
            success=False,
        )


async def get_user_by_email(db: Session, user_email: str):
    try:
        stmt = select(Users).where(Users.email == user_email, Users.is_active)
        result = await db.execute(stmt)
        return result.scalars().first()

    except Exception as err:
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err, exc_info=True)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"{messages.INTERNAL_SERVER_ERROR}",
            success=False,
        )


async def update_user_password(db: Session, user_id: int, hashed_password: str):
    try:
        user = await get_user_by_id(db=db, user_id=user_id)

        if not user:
            raise response_parser.generate_response(
                message="User not found",
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        user.password_hash = hashed_password

        await db.commit()
        await db.refresh(user)

        return user

    except Exception as err:
        logger.exception(
            f"{messages.INTERNAL_SERVER_ERROR} %s",
            err,
            exc_info=True,
        )
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"{messages.INTERNAL_SERVER_ERROR}",
            success=False,
        )


async def get_user_dashboard_details(db: Session, current_user: Users):
    try:
        stats = DashboardStats()

        if current_user.role == UserRole.SUPER_ADMIN:
            stats.total_products = (
                await db.execute(select(func.count(Product.id)))
            ).scalar()
            stats.total_mappings = (
                await db.execute(select(func.count(VendorProductMapping.id)))
            ).scalar()
            stats.total_users = (
                await db.execute(select(func.count(Users.id)))
            ).scalar()

            # Fetch actual records for SuperAdmin
            p_res = await db.execute(select(Product))
            stats.all_products = p_res.scalars().all()

            m_res = await db.execute(select(VendorProductMapping))
            stats.all_mappings = m_res.scalars().all()

        elif current_user.role == UserRole.VENDOR:
            p_res = await db.execute(
                select(Product).where(Product.created_by == current_user.id)
            )
            stats.my_products = p_res.scalars().all()

            m_res = await db.execute(
                select(VendorProductMapping).where(
                    VendorProductMapping.vendor_id == current_user.id
                )
            )
            stats.my_mappings = m_res.scalars().all()

            stats.total_products = len(stats.my_products)
            stats.total_mappings = len(stats.my_mappings)

        details = UserDetails(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            role=current_user.role.value,
            stats=stats,
        )
        return details

    except Exception as err:
        logger.exception(f"{messages.INTERNAL_SERVER_ERROR} %s", err, exc_info=True)
        raise response_parser.generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False,
        )
