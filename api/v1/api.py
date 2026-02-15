from fastapi import APIRouter

from api.v1.endpoint import (
    auth_endpoint,
    vendor_endpoint,
    category_endpoint,
    product_endpoint,
    purchase_endpoint,
    inventory_endpoint,
)

router = APIRouter()

router.include_router(auth_endpoint.auth_router, tags=["Authentication"])
router.include_router(vendor_endpoint.vendor_router, tags=["Vendor"])
router.include_router(category_endpoint.category_router, tags=["Category"])
router.include_router(product_endpoint.product_router, tags=["Product"])
router.include_router(purchase_endpoint.purchase_router, tags=["Purchase Order"])
router.include_router(inventory_endpoint.inventory_router, tags=["Inventory"])
