# Project Setup & Testing Guide

This guide provides step-by-step instructions to clone the repository, set up the environment, initialize the database, and verify application features across different user roles.

---

##  1. Clone the Repository

### 1.1 Clone the Project

```bash
# Clone the repository
git clone https://github.com/smriti117/inventory-management.git

# Navigate into the project directory
cd inventory-management
```

### 1.2 Checkout Correct Branch (If Required)

```bash
git branch          # See current branch
git checkout dev    # Example: switch to dev branch
git pull origin dev # Pull latest changes
```

---

## 2. Environment Setup

### 2.1 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux / Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

---

### 2.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 2.3 Configure Environment Variables

Ensure you have a `.env` file in the root directory.

```bash
cp .env.example .env
```

> Update `DATABASE_URL` if your local PostgreSQL configuration differs.

---

## 3. Database Initialization

### 3.1 Start PostgreSQL (Docker)

```bash
docker-compose up -d
```

Verify containers are running:

```bash
docker ps
```

---

### 3.2 Run Migrations

```bash
alembic upgrade head
```

To fully reset the schema:

```bash
alembic downgrade base
alembic upgrade head
```

---

### 3.3 Cleanup & Seed Data

```bash
# Optional: Clear existing data
python3 scripts/cleanup.py

# Seed SuperAdmin, Vendors, and Customer
python3 scripts/seed.py
```

---

## 4. Run the Application

```bash
uvicorn main:app --reload
```

Open Swagger documentation:

```
http://localhost:8000/docs
```

---

# 5. Role-Based API Testing

Use the following endpoint to obtain authentication tokens:

```
POST /backend/api/v1/auth/login
```

---

## 5.1 SuperAdmin Flow

**Credentials:**

```
superadmin@example.com
password
```

### Expected Capabilities

* Full visibility of system data
* Full CRUD access across modules
* Manage users, products, and categories

### Verification

Call:

```
GET /backend/api/v1/auth/me/details
```

Verify response includes:

* `all_products`
* `all_mappings`

---

## 5.2 Vendor Flow (Strict Isolation)

**Credentials:**

```
Vendor 1: first_vendor@example.com / password
Vendor 2: second_vendor@example.com / password
```

### Goal

Each vendor manages only their own catalog.

### Verification

#### Ownership Restriction

1. Login as Vendor 2
2. Attempt to update Product ID 1 (created by Vendor 1)

**Expected Response:**

```
403 Forbidden
"You can only edit products you created"
```

#### Dashboard Scope

Call:

```
GET /backend/api/v1/auth/me/details
```

Verify response contains only:

* `my_products`

---

## 5.3 Customer Flow (Read-Only Access)

**Credentials:**

```
customer@example.com
password
```

### Allowed Actions

```
GET /backend/api/v1/product/
GET /backend/api/v1/inventory/
```

### Restricted Actions

Attempt:

* Create product
* Update stock

**Expected Response:**

```
403 Forbidden
```

or

```
401 Unauthorized
```

(depending on RBAC implementation)

---

# Final Setup Checklist

* [ ] Repository cloned
* [ ] Correct branch checked out
* [ ] Virtual environment created & activated
* [ ] Dependencies installed
* [ ] `.env` configured
* [ ] Docker containers running
* [ ] Migrations executed
* [ ] Seed data loaded
* [ ] Application running

---

#  Notes

* Ensure Docker is installed before running `docker-compose`.
* Always activate the virtual environment before running project commands.
* If ports are already in use, update configuration accordingly.

---
