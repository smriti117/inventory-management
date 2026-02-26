import asyncio
import os
import uuid
from models.users import Users
from enums.enum_helper import UserRole
from datetime import datetime
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

import pytest
import pytest_asyncio
from fastapi import status

from database.engine import Base, get_db
from models.users import Users
from enums.enum_helper import UserRole
from helpers.token_generator import TokenGenerator
from main import app
from models.category import Category
from models.product import Product
from models.vendor import Vendor



# Set test environment variable
os.environ["PYTEST_CURRENT_TEST"] = "1"
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine):
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(test_db):
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(test_db):
    """Create a test admin user"""
    
    user = Users(
        email=f"admin-{uuid.uuid4()}@example.com",
        first_name="Admin",
        last_name="User",
        password_hash="hashed_password",
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def vendor_user(test_db):
    
    user = Users(
        email=f"vendor-{uuid.uuid4()}@example.com",
        first_name="Vendor",
        last_name="User",
        password_hash="hashed_password",
        role=UserRole.VENDOR,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def customer_user(test_db):
    
    user = Users(
        email=f"customer-{uuid.uuid4()}@example.com",
        first_name="Customer",
        last_name="User",
        password_hash="hashed_password",
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_category(test_db):    
    category = Category(name=f"Test Category-{uuid.uuid4().hex[:8]}")
    test_db.add(category)
    await test_db.commit()
    await test_db.refresh(category)
    return category


@pytest_asyncio.fixture
async def sample_vendor(test_db):
    """Create a sample vendor for testing"""

    vendor = Vendor(
        vendor_code=f"VEND-{uuid.uuid4().hex[:8]}",
        company_name=f"Test Vendor-{uuid.uuid4().hex[:8]}",
        is_active=True
    )
    test_db.add(vendor)
    await test_db.commit()
    await test_db.refresh(vendor)
    return vendor


@pytest_asyncio.fixture
async def sample_product(test_db, admin_user, sample_category):
    """Create a sample product for testing"""
    
    product = Product(
        name=f"Test Product-{uuid.uuid4().hex[:8]}",
        sku=f"PROD-{uuid.uuid4().hex[:8]}",
        category_id=sample_category.id,
        measurement_unit="pcs",
        created_by=admin_user.id
    )
    test_db.add(product)
    await test_db.commit()
    await test_db.refresh(product)
    return product


@pytest_asyncio.fixture
async def authenticated_admin_client(client, admin_user, test_db):
    """Create client with admin authentication"""
    
    # Generate real JWT token for admin user
    token = TokenGenerator.encode_token(admin_user, expire_time_in_mins=60)
    
    client.headers.update({
        "Authorization": f"Bearer {token}"
    })
    yield client
    # Clean up headers
    client.headers.pop("Authorization", None)


@pytest_asyncio.fixture
async def authenticated_vendor_client(client, vendor_user, test_db):
    
    # Generate real JWT token for vendor user
    token = TokenGenerator.encode_token(vendor_user, expire_time_in_mins=60)
    
    client.headers.update({
        "Authorization": f"Bearer {token}"
    })
    yield client
    
    client.headers.pop("Authorization", None)


@pytest_asyncio.fixture
async def authenticated_customer_client(client, customer_user, test_db):
    # Generate real JWT token for customer user
    token = TokenGenerator.encode_token(customer_user, expire_time_in_mins=60)
    
    client.headers.update({
        "Authorization": f"Bearer {token}"
    })
    yield client

    client.headers.pop("Authorization", None)
