import pytest
from fastapi import status
from pydantic import ValidationError


@pytest.mark.asyncio
async def test_login_flow_failure(client):
    """
    Login with non-existent user should return 404
    """
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }

    response = await client.post(
        "/backend/api/v1/auth/login",
        json=login_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    response_data = response.json()
    assert "detail" in response_data
    assert response_data["detail"]["success"] is False
    assert response_data["detail"]["message"] == "User does not exists"


@pytest.mark.asyncio
async def test_login_with_null_email(client):
    """
    Test: Login with null email should return 404 (because schema allows Optional)
    """
    login_data = {
        "email": None,
        "password": "somepassword"
    }

    response = await client.post(
        "/backend/api/v1/auth/login",
        json=login_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    response_data = response.json()
    assert "detail" in response_data
    assert response_data["detail"]["success"] is False
    assert response_data["detail"]["message"] == "User does not exists"


@pytest.mark.asyncio
async def test_login_with_invalid_email_format(client):
    """
    Test: Login with invalid email format
    """
    invalid_emails = [
        "invalid-email",  # Missing @
        "invalid@",      # Missing domain
        "@domain.com",   # Missing local part
        "",             # Empty string (valid Optional[str])
        "   ",           # Whitespace only (valid Optional[str])
    ]

    for invalid_email in invalid_emails:
        response = await client.post(
            "/backend/api/v1/auth/login",
            json={"email": invalid_email, "password": "somepassword"},
        )

        if invalid_email in ["", "   "]:
            assert response.status_code == status.HTTP_404_NOT_FOUND
        else:
            assert response.status_code in [
                status.HTTP_404_NOT_FOUND,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]


@pytest.mark.asyncio
async def test_login_with_null_password(client):
    """
    Test: Login with null password
    """
    login_data = {
        "email": "test@example.com",
        "password": None
    }

    response = await client.post(
        "/backend/api/v1/auth/login",
        json=login_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    response_data = response.json()
    assert "detail" in response_data
    assert response_data["detail"]["success"] is False
    assert response_data["detail"]["message"] == "User does not exists"


@pytest.mark.asyncio
async def test_login_with_missing_fields(client):
    """
    Test: Login with missing required fields
    """
    response = await client.post(
        "/backend/api/v1/auth/login",
        json={"password": "somepassword"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test missing password
    response = await client.post(
        "/backend/api/v1/auth/login",
        json={"email": "test@example.com"},
    )
    # Returns 422 because FastAPI requires the field to be present
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test completely empty payload
    response = await client.post(
        "/backend/api/v1/auth/login",
        json={},  # Empty payload
    )
    # Returns 422 because both fields are missing
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_with_empty_payload(client):
    """
    Test: Login with empty payload (no JSON body)
    """
    response = await client.post("/backend/api/v1/auth/login")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    response_data = response.json()
    assert "detail" in response_data
    assert "field required" in str(response_data["detail"]).lower()

