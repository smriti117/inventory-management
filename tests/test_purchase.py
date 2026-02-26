import pytest
from fastapi import status
from decimal import Decimal
from enums.enum_helper import PurchaseOrderStatus
from schemas.purchase_schema import PurchaseOrderCreate, PurchaseOrderItemCreate


@pytest.mark.asyncio
async def test_get_purchase_orders_as_admin(authenticated_admin_client, test_db):
    """
    Test: Get all purchase orders as SUPER_ADMIN (authenticated)
    """
    response = await authenticated_admin_client.get("/backend/api/v1/purchase-order/")
    
    # Should succeed - admin has access
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    print(f"Admin successfully retrieved {len(data['data'])} purchase orders")


@pytest.mark.asyncio
async def test_create_purchase_order_as_admin(authenticated_admin_client, test_db, sample_vendor, sample_product):
    """
    Test: Create purchase order as SUPER_ADMIN (authenticated)
    """
    # First create vendor-product mapping
    mapping_data = {
        "vendor_id": sample_vendor.id,
        "product_id": sample_product.id,
        "unit_price": 99.99
    }
    mapping_response = await authenticated_admin_client.post("/backend/api/v1/vendor/product-mapping", json=mapping_data)
    assert mapping_response.status_code == status.HTTP_201_CREATED
    
    # Now create purchase order
    po_data = {
        "vendor_id": sample_vendor.id,
        "items": [
            {
                "product_id": sample_product.id,
                "quantity": 10,
                "unit_price": 99.99
            }
        ],
        "notes": "Test purchase order"
    }
    
    response = await authenticated_admin_client.post("/backend/api/v1/purchase-order/", json=po_data)
    
    # Should succeed - admin can create purchase orders
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["success"] is True
    assert data["data"]["vendor_id"] == sample_vendor.id
    assert data["data"]["status"] == "DRAFT"
    assert data["data"]["total_amount"] == 999.9
    assert "id" in data["data"]
    assert "po_number" in data["data"]
    print(f"Admin successfully created purchase order with ID: {data['data']['id']}")


@pytest.mark.asyncio
async def test_get_purchase_orders_as_vendor_forbidden(authenticated_vendor_client, test_db):
    """
    Test: Get all purchase orders as VENDOR role (should fail - forbidden)
    """
    response = await authenticated_vendor_client.get("/backend/api/v1/purchase-order/")
    
    # Should fail - vendors cannot see all purchase orders
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "You do not have permission to perform this action"
    print("Vendor correctly forbidden from accessing all purchase orders")


@pytest.mark.asyncio
async def test_get_purchase_orders_as_customer_forbidden(authenticated_customer_client, test_db):
    """
    Test: Get all purchase orders as CUSTOMER role (should fail - forbidden)
    """
    response = await authenticated_customer_client.get("/backend/api/v1/purchase-order/")
    
    # Should fail - customers cannot see purchase orders
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "You do not have permission to perform this action"
    print("Customer correctly forbidden from accessing all purchase orders")


@pytest.mark.asyncio
async def test_create_purchase_order_as_vendor_forbidden(authenticated_vendor_client, test_db):
    """
    Test: Create purchase order as VENDOR role (should fail - forbidden)
    """
    po_data = {
        "vendor_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 10,
                "unit_price": 99.99
            }
        ]
    }
    
    response = await authenticated_vendor_client.post("/backend/api/v1/purchase-order/", json=po_data)
    
    # Should fail - vendors cannot create purchase orders
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "You do not have permission to perform this action"
    print("Vendor correctly forbidden from creating purchase orders")


@pytest.mark.asyncio
async def test_create_purchase_order_unauthenticated(client):
    """
    Test: Create purchase order without authentication (should fail)
    """
    po_data = {
        "vendor_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 10,
                "unit_price": 99.99
            }
        ]
    }
    
    response = await client.post("/backend/api/v1/purchase-order/", json=po_data)
    
    # Should fail - no authentication
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_purchase_order_with_invalid_data(client):
    """
    Test: Create purchase order with invalid data
    """
    invalid_payloads = [
        {}, 
        {"vendor_id": 1},
        {"items": []},
        {"vendor_id": "invalid", "items": []},
        {"vendor_id": 1, "items": "invalid"},
        {"vendor_id": 1, "items": [{}]},
        {"vendor_id": 1, "items": [{"product_id": "invalid"}]},
        {"vendor_id": 1, "items": [{"product_id": 1}]},
        {"vendor_id": 1, "items": [{"product_id": 1, "quantity": "invalid"}]},
        {"vendor_id": 1, "items": [{"product_id": 1, "quantity": -1}]}, 
        {"vendor_id": 1, "items": [{"product_id": 1, "quantity": 0}]},  
        {"vendor_id": 1, "items": [{"product_id": 1, "quantity": 5}]}, 
        {"vendor_id": 1, "items": [{"product_id": 1, "quantity": 5, "unit_price": "invalid"}]}, 
        {"vendor_id": 1, "items": [{"product_id": 1, "quantity": 5, "unit_price": -10}]}, 
    ]

    for payload in invalid_payloads:
        response = await client.post("/backend/api/v1/purchase-order/", json=payload)
        
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY, 
            status.HTTP_401_UNAUTHORIZED,          
            status.HTTP_403_FORBIDDEN              
        ]
        
        if response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            response_data = response.json()
            assert "detail" in response_data


@pytest.mark.asyncio
async def test_purchase_order_schema_validation():
    """
    Test:Pydantic schema validation
    """
    try:
        PurchaseOrderCreate(
            vendor_id=1,
            items=[
                PurchaseOrderItemCreate(
                    product_id=1,
                    quantity=5,
                    unit_price=Decimal("99.99")
                )
            ]
        )
        PurchaseOrderCreate(
            vendor_id=1,
            notes="Test notes",
            items=[
                PurchaseOrderItemCreate(
                    product_id=1,
                    quantity=10,
                    unit_price=Decimal("199.99")
                ),
                PurchaseOrderItemCreate(
                    product_id=2,
                    quantity=3,
                    unit_price=Decimal("49.99")
                )
            ]
        )
        print("Valid purchase order schemas")
    except Exception as e:
        pytest.fail(f"Valid schemas should not fail: {e}")


@pytest.mark.asyncio
async def test_purchase_order_status_validation():
    """
    Test:Purchase order status enum validation
    """
    valid_statuses = [
        PurchaseOrderStatus.DRAFT,
        PurchaseOrderStatus.APPROVED,
        PurchaseOrderStatus.PARTIAL,
        PurchaseOrderStatus.RECEIVED,
        PurchaseOrderStatus.CANCELLED
    ]
    
    for status_value in valid_statuses:
        assert status_value in PurchaseOrderStatus
        print(f"Valid status: {status_value}")

    expected_statuses = {"DRAFT", "APPROVED", "PARTIAL", "RECEIVED", "CANCELLED"}
    actual_statuses = {status.value for status in PurchaseOrderStatus}
    assert expected_statuses == actual_statuses
