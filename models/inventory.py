from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Integer,
)
from sqlalchemy.orm import relationship
from database.engine import Base
from enums.enum_helper import InventoryTransactionType


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    transaction_type = Column(SQLEnum(InventoryTransactionType), nullable=False)

    reference_id = Column(Integer)
    reference_type = Column(String(50))

    quantity_change = Column(Integer, nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    current_quantity = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=0)

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    product = relationship("Product")
