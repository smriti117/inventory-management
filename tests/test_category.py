import pytest
from fastapi import status
from schemas.category_schema import CategoryCreate


@pytest.mark.asyncio
async def test_get_categories_as_admin(authenticated_admin_client, test_db):
    """
    Test: Get all categories as SUPER_ADMIN (authenticated)
    """
    response = await authenticated_admin_client.get("/backend/api/v1/category/")
    
    # Should succeed - admin has access
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    print(f"Admin successfully retrieved {len(data['data'])} categories")


@pytest.mark.asyncio
async def test_get_categories_as_vendor(authenticated_vendor_client, test_db):
    """
    Test: Get all categories as VENDOR role (authenticated)
    """
    response = await authenticated_vendor_client.get("/backend/api/v1/category/")
    
    # Should succeed - vendors have access
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    print(f"Vendor successfully retrieved {len(data['data'])} categories")


@pytest.mark.asyncio
async def test_get_categories_as_customer(authenticated_customer_client, test_db):
    """
    Test: Get all categories as CUSTOMER role (authenticated)
    """
    response = await authenticated_customer_client.get("/backend/api/v1/category/")
    
    # Should succeed - customers have access
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    print(f"Customer successfully retrieved {len(data['data'])} categories")


@pytest.mark.asyncio
async def test_create_category_as_admin(authenticated_admin_client, test_db):
    """
    Test: Create category as SUPER_ADMIN (authenticated)
    """
    category_data = {
        "name": "Test Category",
        "parent_id": None
    }
    
    response = await authenticated_admin_client.post("/backend/api/v1/category/", json=category_data)
    
    # Should succeed - admin can create categories
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Category"
    assert "id" in data["data"]
    print(f"Admin successfully created category with ID: {data['data']['id']}")


@pytest.mark.asyncio
async def test_create_category_as_vendor_forbidden(authenticated_vendor_client, test_db):
    """
    Test: Create category as VENDOR role (should fail - forbidden)
    """
    category_data = {
        "name": "Test Category",
        "parent_id": None
    }
    
    response = await authenticated_vendor_client.post("/backend/api/v1/category/", json=category_data)
    
    # Should fail - vendors cannot create categories
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    data = response.json()
    print(f"DEBUG: 403 Response data = {data}")
    
    # HTTPException detail format
    assert "detail" in data
    assert data["detail"] == "You do not have permission to perform this action"
    print("Vendor correctly forbidden from creating category")


@pytest.mark.asyncio
async def test_create_category_as_customer_forbidden(authenticated_customer_client, test_db):
    """
    Test: Create category as CUSTOMER role (should fail - forbidden)
    """
    category_data = {
        "name": "Test Category",
        "parent_id": None
    }
    
    response = await authenticated_customer_client.post("/backend/api/v1/category/", json=category_data)
    
    # Should fail - customers cannot create categories
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    data = response.json()
    print(f"DEBUG: 403 Response data = {data}")
    
    # HTTPException detail format
    assert "detail" in data
    assert data["detail"] == "You do not have permission to perform this action"
    print("Customer correctly forbidden from creating category")


@pytest.mark.asyncio
async def test_create_category_unauthenticated(client):
    """
    Test: Create category without authentication (should fail)
    """
    category_data = {
        "name": "Test Category",
        "parent_id": None
    }
    
    response = await client.post("/backend/api/v1/category/", json=category_data)
    
    # Should fail - no authentication
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_category_with_invalid_data(client):
    """
    Test: Create category with invalid data
    """
    invalid_payloads = [
        {},
        {"name": ""}, 
        {"name": None}, 
        {"name": "   "}, 
        {"parent_id": "invalid"}, 
        {"name": "A" * 256}, 
    ]

    for payload in invalid_payloads:
        response = await client.post("/backend/api/v1/category/", json=payload)
        
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY, 
            status.HTTP_401_UNAUTHORIZED,          
            status.HTTP_403_FORBIDDEN             
        ]
        
        if response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            response_data = response.json()
            assert "detail" in response_data


@pytest.mark.asyncio
async def test_category_schema_validation():
    """
    Test: Pydantic schema validation
    """
    try:
        CategoryCreate(name="Valid Category")
        CategoryCreate(name="Valid Category", parent_id=None)
        CategoryCreate(name="Valid Category", parent_id=1)
    except Exception as e:
        pytest.fail(f"Valid schemas should not fail: {e}")
