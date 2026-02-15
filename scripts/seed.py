import asyncio
import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from database.engine import AsyncSessionLocal
from database.security import get_password_hash
from models.users import Users
from models.vendor import Vendor, VendorLocation, VendorBankDetail
from models.product import Product, VendorProductMapping
from models.category import Category
from enums.enum_helper import UserRole


async def seed_data():
    async with AsyncSessionLocal() as session:
        # 1. Seed Categories
        categories_data = [
            {"name": "Electronics"},
            {"name": "Stationery"},
            {"name": "Furniture"},
        ]

        categories = {}
        for cat_data in categories_data:
            stmt = select(Category).where(Category.name == cat_data["name"])
            result = await session.execute(stmt)
            cat = result.scalar_one_or_none()
            if not cat:
                cat = Category(name=cat_data["name"])
                session.add(cat)
                await session.flush()
            categories[cat_data["name"]] = cat

        # 2. Seed Users
        users_data = [
            {
                "email": "superadmin@example.com",
                "first_name": "superadmin",
                "last_name": "superadmin",
                "password": "password",
                "role": UserRole.SUPER_ADMIN,
            },
            {
                "email": "first_vendor@example.com",
                "first_name": "First",
                "last_name": "Vendor",
                "password": "password",
                "role": UserRole.VENDOR,
            },
            {
                "email": "second_vendor@example.com",
                "first_name": "Second",
                "last_name": "Vendor",
                "password": "password",
                "role": UserRole.VENDOR,
            },
            {
                "email": "customer@example.com",
                "first_name": "customer",
                "last_name": "customer",
                "password": "password",
                "role": UserRole.CUSTOMER,
            },
        ]

        users = {}
        for u_data in users_data:
            stmt = select(Users).where(Users.email == u_data["email"])
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if not user:
                user = Users(
                    email=u_data["email"],
                    first_name=u_data["first_name"],
                    last_name=u_data["last_name"],
                    role=u_data["role"],
                    password_hash=get_password_hash(u_data["password"]),
                    is_active=True,
                )
                session.add(user)
                await session.flush()
            users[u_data["email"]] = user

        # 3. Seed Vendors
        vendors_data = [
            {
                "vendor_code": "VEND001",
                "company_name": "First Vendor Corp",
                "is_active": True,
            },
            {
                "vendor_code": "VEND002",
                "company_name": "Second Vendor Corp",
                "is_active": True,
            },
        ]

        vendors = {}
        for v_data in vendors_data:
            stmt = select(Vendor).where(Vendor.vendor_code == v_data["vendor_code"])
            result = await session.execute(stmt)
            vendor = result.scalar_one_or_none()
            if not vendor:
                vendor = Vendor(
                    vendor_code=v_data["vendor_code"],
                    company_name=v_data["company_name"],
                    is_active=v_data["is_active"],
                )
                session.add(vendor)
                await session.flush()

                # Add location
                location = VendorLocation(
                    vendor_id=vendor.id,
                    address_line1=f"Address for {vendor.company_name}",
                    city="Mumbai",
                    state="Maharashtra",
                    country="India",
                    postal_code="400001",
                    is_primary=True,
                )
                session.add(location)

                # Add bank details
                bank = VendorBankDetail(
                    vendor_id=vendor.id,
                    bank_name="Axis Bank",
                    account_number=f"ACC_{vendor.vendor_code}",
                    ifsc_code="AXIS0001234",
                    is_primary=True,
                )
                session.add(bank)
                await session.flush()
            vendors[v_data["vendor_code"]] = vendor

        # 4. Seed Products
        products_data = [
            {
                "sku": "SKU-LAP-001",
                "name": "First Vendor Laptop",
                "category": "Electronics",
                "measurement_unit": "Piece",
                "vendor_code": "VEND001",
                "unit_price": 1200.00,
                "created_by": "first_vendor@example.com",
            },
            {
                "sku": "SKU-NOTE-001",
                "name": "Second Vendor Notebook",
                "category": "Stationery",
                "measurement_unit": "Dozen",
                "vendor_code": "VEND002",
                "unit_price": 25.50,
                "created_by": "second_vendor@example.com",
            },
        ]

        for p_data in products_data:
            stmt = select(Product).where(Product.sku == p_data["sku"])
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            if not product:
                product = Product(
                    sku=p_data["sku"],
                    name=p_data["name"],
                    category_id=categories[p_data["category"]].id,
                    measurement_unit=p_data["measurement_unit"],
                    created_by=users[p_data["created_by"]].id,
                    is_active=True,
                )
                session.add(product)
                await session.flush()

                # Map to vendor
                mapping = VendorProductMapping(
                    vendor_id=vendors[p_data["vendor_code"]].id,
                    product_id=product.id,
                    vendor_sku=f"V-{p_data['sku']}",
                    unit_price=p_data["unit_price"],
                    min_order_quantity=1,
                )
                session.add(mapping)

        await session.commit()
        print("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
