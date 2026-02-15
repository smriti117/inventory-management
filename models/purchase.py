from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Integer,
    Numeric,
    Text,
)
from sqlalchemy.orm import relationship
from database.engine import Base
from enums.enum_helper import PurchaseOrderStatus


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    po_number = Column(String(100), unique=True, nullable=False, index=True)

    vendor_id = Column(
        Integer,
        ForeignKey("vendors.id"),
        nullable=False,
        index=True,
    )

    status = Column(
        SQLEnum(PurchaseOrderStatus),
        nullable=False,
        default=PurchaseOrderStatus.DRAFT,
    )

    total_amount = Column(Numeric(12, 2), nullable=True)
    notes = Column(Text, nullable=True)

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    items = relationship("PurchaseOrderItem", back_populates="purchase_order")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    purchase_order_id = Column(
        Integer, ForeignKey("purchase_orders.id"), nullable=False
    )

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    ordered_quantity = Column(Integer, nullable=False)
    received_quantity = Column(Integer, default=0, nullable=False)

    unit_price = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
