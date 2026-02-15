# Comprehensive Setup & Testing Guide

This guide provides step-by-step instructions to set up the environment, initialize the database, and verify the application features across different user roles.

---
# Clone the Repository
git clone https://github.com/smriti117/inventory-management.git

# Navigate into the project directory
cd inventory-management

1.1 Checkout Correct Branch (If Required)
git branch          # See current branch
git checkout dev    # Example: switch to dev branch
git pull origin dev # Pull latest changes


## Setup :  Environment Setup

### 1.1 Virtual Environment
Create and activate a Python virtual environment to isolate dependencies:
```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate
```

### 1.2 Install Requirements
Install all core and development dependencies:
```bash
pip install -r requirements.txt
```

### 1.3 Environment Variables
Ensure you have a `.env` file in the root directory. You can use the provided `.env.example` as a template:
```bash
cp .env.example .env
```
*Note: Update `DATABASE_URL` if your local PostgreSQL settings differ.*

---

## Step 2: Database Initialization

### 2.1 Start PostgreSQL
We recommend using Docker Compose to start the database and pgAdmin:
```bash
docker-compose up -d
```

### 2.2 Run Migrations
Use Alembic to create the database schema from scratch:
```bash
alembic upgrade head
```

### 2.3 Cleanup & Seed Data
Execute the cleanup script to reset sequences and then seed the test data:
```bash
# Seed SuperAdmin, Vendors, and Customer
python3 scripts/seed.py
```

---

## Step 3: Running the Application
Start the FastAPI server:
```bash
uvicorn main:app --reload
```
Open the API documentation at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Step 4: Role-Based API Testing

Use the `/backend/api/v1/auth/login` endpoint to get tokens for each role.

### 4.1 SuperAdmin Flow
- **Credentials**: `superadmin@example.com` / `password`
- **Goal**: Full visibility and system management.
- **Verification**:
    - Call `GET /backend/api/v1/auth/me/details`. Verify you see `all_products` and `all_mappings`.
    - Create/Delete any user or category.

### 4.2 Vendor Flow (Strict Isolation)
- **Credentials**: 
    - **Vendor 1**: `first_vendor@example.com` / `password`
    - **Vendor 2**: `second_vendor@example.com` / `password`
- **Goal**: Manage independent catalogs.
- **Verification**:
    - **Ownership**: Login as Vendor 2. Try to update a product owned by Vendor 1 (ID 1). 
        - *Expected*: `403 Forbidden` - "You can only edit products you created".
    - **Dashboard**: Call `GET /backend/api/v1/auth/me/details`. Verify you only see `my_products` (the ones you created).

### 4.3 Customer Flow (Read-Only)
- **Credentials**: `customer@example.com` / `password`
- **Goal**: Browse availability.
- **Verification**:
    - **Read Permission**: Can call `GET /backend/api/v1/product/` and `GET /backend/api/v1/inventory/`.
    - **Write Restriction**: Try to create a product or update stock. 
        - *Expected*: `403 Forbidden` or `Unauthorized` based on RBAC.

---
