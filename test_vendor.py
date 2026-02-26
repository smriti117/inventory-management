import pytest
from fastapi import status
from schemas.vendor_schema import VendorCreate, VendorLocationCreate


@pytest.mark.asyncio
async def test_get_vendors_as_admin(authenticated_admin_client, test_db):
    """
    Test: Get all vendors as SUPER_ADMIN (authenticated)
    """
    response = await authenticated_admin_client.get("/backend/api/v1/vendor/")
    
    # Should succeed - admin has access
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    print(f"Admin successfully retrieved {len(data['data'])} vendors")


@pytest.mark.asyncio
async def test_create_vendor_as_admin(authenticated_admin_client, test_db):
    """
    Test: Create vendor as SUPER_ADMIN (authenticated)
    """
    vendor_data = {
        "company_name": "Test Vendor Company",
        "is_active": True,
        "locations": [
            {
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state": "Test State",
                "country": "Test Country",
                "postal_code": "12345",
                "is_primary": True
            }
        ]
    }
    
    response = await authenticated_admin_client.post("/backend/api/v1/vendor/", json=vendor_data)
    
    # Should succeed - admin can create vendors
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["success"] is True
    assert data["data"]["company_name"] == "Test Vendor Company"
    assert "id" in data["data"]
    print(f"Admin successfully created vendor with ID: {data['data']['id']}")


@pytest.mark.asyncio
async def test_get_vendors_as_vendor_forbidden(authenticated_vendor_client, test_db):
    """
    Test: Get all vendors as VENDOR role (should fail - forbidden)
    """
    response = await authenticated_vendor_client.get("/backend/api/v1/vendor/")
    
    # Should fail - vendors cannot see all vendors
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "You do not have permission to perform this action"
    print("Vendor correctly forbidden from accessing all vendors")


@pytest.mark.asyncio
async def test_create_vendor_as_vendor_forbidden(authenticated_vendor_client, test_db):
    """
    Test: Create vendor as VENDOR role (should fail - forbidden)
    """
    vendor_data = {
        "company_name": "Test Vendor Company",
        "is_active": True
    }
    
    response = await authenticated_vendor_client.post("/backend/api/v1/vendor/", json=vendor_data)
    
    # Should fail - vendors cannot create vendors
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "You do not have permission to perform this action"
    print("Vendor correctly forbidden from creating vendors")


@pytest.mark.asyncio
async def test_create_vendor_unauthenticated(client):
    """
    Test: Create vendor without authentication (should fail)
    """
    vendor_data = {
        "company_name": "Test Vendor Company",
        "is_active": True
    }
    
    response = await client.post("/backend/api/v1/vendor/", json=vendor_data)
    
    # Should fail - no authentication (FastAPI returns 403 for missing Authorization header)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_vendor_with_invalid_data(client):
    """
    Test: Create vendor with invalid data
    """
    invalid_payloads = [
        {},
        {"company_name": ""},
        {"company_name": None},
        {"company_name": "   "},
        {"company_name": "A" * 256},
        {"company_name": "Test", "is_active": "invalid"},
        {"company_name": "Test", "locations": "invalid"}
    ]

    for payload in invalid_payloads:
        response = await client.post("/backend/api/v1/vendor/", json=payload)
        
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN
        ]
        
        if response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            response_data = response.json()
            assert "detail" in response_data


@pytest.mark.asyncio
async def test_vendor_schema_validation():
    """
    Test: Pydantic schema validation
    """
    try:
        VendorCreate(company_name="Valid Vendor")
        VendorCreate(company_name="Valid Vendor", is_active=False)
        VendorCreate(
            company_name="Valid Vendor",
            is_active=True,
            locations=[
                VendorLocationCreate(
                    address_line1="123 Main St",
                    city="Test City",
                    state="Test State",
                    country="Test Country",
                    postal_code="12345",
                    is_primary=True
                )
            ]
        )
    except Exception as e:
        pytest.fail(f"Valid schemas should not fail: {e}")

    try:
        VendorLocationCreate(
            address_line1="123 Main St",
            city="Test City", 
            state="Test State",
            country="Test Country",
            postal_code="12345"
        )
    except Exception as e:
        pytest.fail(f"Valid location schemas should not fail: {e}")
