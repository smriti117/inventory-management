"""
Models package - Database models for the inventory management system.

All models are imported here for Alembic to discover them during migrations.
"""

from database.engine import Base

# Import all models
from models.users import Users
from models.vendor import Vendor, VendorLocation, VendorCompliance, VendorBankDetail
from models.product import Product, VendorProductMapping
from models.category import Category
from models.inventory import InventoryTransaction
from models.purchase import PurchaseOrder, PurchaseOrderItem
from enums.enum_helper import (
    UserRole,
    PurchaseOrderStatus,
    InventoryTransactionType,
)

__all__ = [
    "Base",
    "Users",
    "UserRole",
    "Vendor",
    "VendorLocation",
    "VendorCompliance",
    "VendorBankDetail",
    "Product",
    "VendorProductMapping",
    "Category",
    "InventoryTransaction",
    "InventoryTransactionType",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "PurchaseOrderStatus",
]
