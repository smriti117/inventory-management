from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.engine import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    vendor_code = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    locations = relationship("VendorLocation", back_populates="vendor")
    compliances = relationship("VendorCompliance", back_populates="vendor")
    bank_details = relationship("VendorBankDetail", back_populates="vendor")
    products = relationship("VendorProductMapping", back_populates="vendor")


class VendorLocation(Base):
    __tablename__ = "vendor_locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    vendor_id = Column(
        Integer,
        ForeignKey("vendors.id"),
        nullable=False,
        index=True,
    )

    address_line1 = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)

    is_primary = Column(Boolean, default=False, nullable=False)

    vendor = relationship("Vendor", back_populates="locations")


class VendorCompliance(Base):
    __tablename__ = "vendor_compliances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    compliance_type = Column(String(50), nullable=False)
    compliance_number = Column(String(100), nullable=False)

    valid_from = Column(DateTime(timezone=True))
    valid_to = Column(DateTime(timezone=True))

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    vendor = relationship("Vendor", back_populates="compliances")


class VendorBankDetail(Base):
    __tablename__ = "vendor_bank_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    bank_name = Column(String(150), nullable=False)
    account_number = Column(String(50), nullable=False)
    ifsc_code = Column(String(20), nullable=False)
    tax_id = Column(String(50))

    is_primary = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    vendor = relationship("Vendor", back_populates="bank_details")
