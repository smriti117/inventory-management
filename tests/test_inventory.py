import pytest
from fastapi import status
from enums.enum_helper import InventoryTransactionType
from schemas.inventory_schema import StockBase, InventoryTransactionBase


@pytest.mark.asyncio
async def test_get_stocks_as_admin(authenticated_admin_client, test_db):
    """
    Test: Get all stocks as SUPER_ADMIN (authenticated)
    """
    response = await authenticated_admin_client.get("/backend/api/v1/inventory/stock")
    
    # Should succeed - admin has access
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    # API returns wrapped response: {"data": [], "message": "...", "status_code": 200, "success": True}
    assert data["success"] is True
    assert isinstance(data["data"], list)
    print(f"Admin successfully retrieved {len(data['data'])} stock items")


@pytest.mark.asyncio
async def test_get_stocks_as_vendor(authenticated_vendor_client, test_db):
    """
    Test: Get all stocks as VENDOR role (authenticated)
    """
    response = await authenticated_vendor_client.get("/backend/api/v1/inventory/stock")
    
    # Should succeed - vendors have access
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    print(f"Vendor successfully retrieved {len(data['data'])} stock items")


@pytest.mark.asyncio
async def test_get_stocks_as_customer(authenticated_customer_client, test_db):
    """
    Test: Get all stocks as CUSTOMER role (authenticated)
    """
    response = await authenticated_customer_client.get("/backend/api/v1/inventory/stock")
    
    # Should succeed - customers have access
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    print(f"Customer successfully retrieved {len(data['data'])} stock items")


@pytest.mark.asyncio
async def test_get_stocks_unauthenticated(client):
    """
    Test: Get stocks without authentication (should fail)
    """
    response = await client.get("/backend/api/v1/inventory/stock")
    
    # Should fail - no authentication
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_inventory_transaction_types():
    """
    Test: Inventory transaction type enum validation
    """
    valid_types = [
        InventoryTransactionType.INBOUND,
        InventoryTransactionType.OUTBOUND,
        InventoryTransactionType.PURCHASE,
        InventoryTransactionType.SALE,
        InventoryTransactionType.RETURN,
        InventoryTransactionType.ADJUSTMENT
    ]
    
    for transaction_type in valid_types:
        assert transaction_type in InventoryTransactionType
    expected_types = {"INBOUND", "OUTBOUND", "PURCHASE", "SALE", "RETURN", "ADJUSTMENT"}
    actual_types = {t.value for t in InventoryTransactionType}
    assert expected_types == actual_types


@pytest.mark.asyncio
async def test_inventory_schema_validation():
    """
    Test: Pydantic schema validation for inventory
    """
    try:
        StockBase(
            product_id=1,
            current_quantity=100,
            reorder_level=10
        )
        StockBase(
            product_id=1,
            current_quantity=0,
            reorder_level=0
        )
    except Exception as e:
        pytest.fail(f"Valid stock schemas should not fail: {e}")

    try:
        InventoryTransactionBase(
            product_id=1,
            transaction_type=InventoryTransactionType.PURCHASE,
            quantity_change=50
        )
        InventoryTransactionBase(
            product_id=1,
            transaction_type=InventoryTransactionType.SALE,
            quantity_change=-10,
            reference_id=123,
            reference_type="purchase_order"
        )
    except Exception as e:
        pytest.fail(f"Valid transaction schemas should not fail: {e}")

    invalid_stock_cases = [
        {"product_id": "invalid"},
        {"product_id": 1, "current_quantity": "invalid"},
        {"product_id": 1, "current_quantity": 100, "reorder_level": "invalid"},
    ]

    for case in invalid_stock_cases:
        try:
            StockBase(**case)
            pytest.fail(f"Invalid stock case should have failed: {case}")
        except Exception:
            pass

    invalid_transaction_cases = [
        {},  
        {"product_id": "invalid"},  
        {"product_id": 1},  
        {"product_id": 1, "transaction_type": "invalid"},
        {"product_id": 1, "transaction_type": InventoryTransactionType.PURCHASE},
        {"product_id": 1, "transaction_type": InventoryTransactionType.PURCHASE, "quantity_change": "invalid"},
    ]

    for case in invalid_transaction_cases:
        try:
            InventoryTransactionBase(**case)
            pytest.fail(f"Invalid transaction case should have failed: {case}")
        except Exception:
            pass
