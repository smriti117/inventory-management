import pytest
from models.users import Users
from models.category import Category
from enums.enum_helper import UserRole
from services.product_service import create_product, get_all_products
from schemas.product_schema import ProductCreate


@pytest.mark.asyncio
async def test_create_product(test_db):
    import uuid
    category = Category(name=f"Test Category-{uuid.uuid4().hex[:8]}")
    test_db.add(category)
    await test_db.flush()

    user = Users(
        email=f"test_creator-{uuid.uuid4().hex[:8]}@example.com",
        first_name="Test",
        last_name="Creator",
        password_hash="hashed_password",
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    product_data = ProductCreate(
        name=f"Test Product-{uuid.uuid4().hex[:8]}",
        sku=f"TEST-SKU-{uuid.uuid4().hex[:8].upper()}",
        category_id=category.id,
        description="A test product",
        measurement_unit="pcs",
    )

    new_product = await create_product(test_db, product_data, user.id)

    assert new_product.id is not None
    assert new_product.name.startswith("Test Product-")
    assert new_product.created_by == user.id


@pytest.mark.asyncio
async def test_get_all_products(test_db):
    products = await get_all_products(test_db)
    assert isinstance(products, list)
