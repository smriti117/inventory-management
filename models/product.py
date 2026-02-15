from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from database.engine import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )

    measurement_unit = Column(String(50), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

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

    vendor_products = relationship("VendorProductMapping", back_populates="product")


class VendorProductMapping(Base):
    __tablename__ = "vendor_product_mapping"

    __table_args__ = (
        UniqueConstraint("vendor_id", "product_id", name="uq_vendor_product"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    vendor_sku = Column(String(100))
    min_order_quantity = Column(Integer)
    unit_price = Column(Numeric(12, 2))
    days_to_delivery = Column(Integer)

    is_preferred = Column(Boolean, default=False, nullable=False)

    vendor = relationship("Vendor", back_populates="products")
    product = relationship("Product", back_populates="vendor_products")
