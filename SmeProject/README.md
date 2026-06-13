# SME Inventory Management System

A comprehensive Django REST API for managing inventory, products, suppliers, categories, and orders with JWT authentication. Designed for Small and Medium-sized Enterprises (SMEs) to streamline inventory operations.

**Version**: 1.0.0  
**Python**: 3.11+  
**Database**: PostgreSQL (configurable)  
**Framework**: Django 5.2.12 with Django REST Framework

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Requirements](#requirements)
5. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Database Setup](#database-setup)
   - [Python Environment Setup](#python-environment-setup)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [Database Models](#database-models)
9. [Authentication](#authentication)
10. [API Endpoints](#api-endpoints)
11. [API Examples](#api-examples)
12. [Admin Interface](#admin-interface)
13. [Testing](#testing)
14. [Troubleshooting](#troubleshooting)
15. [Development Notes](#development-notes)

---

## Overview

The SME Inventory Management System is a REST API built with Django and Django REST Framework. It provides endpoints for managing inventory across multiple locations, tracking product stock levels, managing suppliers and categories, and creating/viewing orders. The system includes JWT-based authentication for secure API access.

---

## Features

- ✅ **Product Management**: Add, update, retrieve, and delete products
- ✅ **Category Management**: Organize products by categories
- ✅ **Supplier Management**: Manage supplier information and contacts
- ✅ **Inventory Tracking**: Track stock levels and set reorder thresholds
- ✅ **Low-Stock Alerts**: Automatic alerts when product stock falls below reorder level
- ✅ **Order Management**: Create and manage orders with multiple items
- ✅ **JWT Authentication**: Secure API access with JWT tokens
- ✅ **Admin Dashboard**: Django admin interface for management
- ✅ **RESTful Design**: Standard HTTP methods for CRUD operations

---

## Project Structure

```
e:\Projects\SME-Inventory-Management-System\SmeProject/
├── manage.py                    # Django CLI entry point
├── db.sqlite3                   # SQLite database (development)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── SmeProject/                  # Main Django project configuration
│   ├── __init__.py
│   ├── settings.py              # Django settings (DB, installed apps, middleware)
│   ├── urls.py                  # Root URL routing
│   ├── asgi.py                  # ASGI configuration
│   └── wsgi.py                  # WSGI configuration
│
├── SmeApp/                      # Main inventory application
│   ├── __init__.py
│   ├── admin.py                 # Django admin configuration
│   ├── apps.py                  # App configuration
│   ├── models.py                # Database models (Product, Order, Supplier, etc.)
│   ├── serializers.py           # DRF serializers for API
│   ├── views.py                 # API views (endpoints)
│   ├── urls.py                  # App URL routing
│   ├── tests.py                 # Unit tests
│   └── migrations/              # Database migrations
│       ├── __init__.py
│       └── 0001_initial.py      # Initial migration
│
└── Templates/                   # HTML templates (optional)
```

---

## Requirements

### System Requirements
- **OS**: Windows 10/11, macOS, or Linux
- **Python**: 3.11 or higher
- **Database**: PostgreSQL 12+ or SQLite (default)
- **RAM**: Minimum 2GB (recommended 4GB+)
- **Disk Space**: 500MB

### Python Dependencies
- Django 5.2.12
- Django REST Framework 3.17.1
- djangorestframework-simplejwt 5.5.1
- psycopg2-binary 2.9.12 (for PostgreSQL support)

---

## Installation

### Prerequisites

1. **Python 3.11+**: Download from [python.org](https://www.python.org/downloads/)
2. **PostgreSQL** (Optional): Download from [postgresql.org](https://www.postgresql.org/download/)
3. **Git**: Download from [git-scm.com](https://git-scm.com/download/)

### Database Setup

#### Option 1: PostgreSQL (Recommended for Production)

1. **Install PostgreSQL** and ensure it's running
2. **Create database and user**:

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE inventory_db;

-- Create user
CREATE USER postgres WITH PASSWORD 'password';

-- Grant privileges
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET default_transaction_deferrable TO on;
ALTER ROLE postgres SET default_transaction_level TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO postgres;

-- Exit psql
\q
```

Current PostgreSQL configuration in `SmeProject/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventory_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### Option 2: SQLite (Default for Development)

SQLite is already configured. Migrations will create `db.sqlite3` automatically.

### Python Environment Setup

1. **Navigate to project directory**:
```bash
cd e:\Projects\SME-Inventory-Management-System\SmeProject
```

2. **Create virtual environment** (Windows):
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

Or on macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run migrations**:
```bash
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, SmeApp
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying sessions.0001_initial... OK
  Applying SmeApp.0001_initial... OK
```

5. **Create superuser** (for admin access):
```bash
python manage.py createsuperuser
```

Follow the prompts:
```
Username: admin
Email: admin@example.com
Password: (enter your secure password)
Password (again): (confirm password)
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```bash
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

### Django Settings

Key settings in `SmeProject/settings.py`:

```python
# Debug mode (set to False in production)
DEBUG = True

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'SmeApp',
]

# JWT Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

---

## Running the Application

### Start Development Server

```bash
python manage.py runserver
```

Or specify a custom port:
```bash
python manage.py runserver 8001
```

**Output**:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
June 13, 2026 - 10:00:00
Django version 5.2.12, using settings 'SmeProject.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Access the Application

- **API Root**: http://127.0.0.1:8000/api/
- **Admin Interface**: http://127.0.0.1:8000/admin/
- **API Token Endpoint**: http://127.0.0.1:8000/api/token/

---

## Database Models

### Category
Represents product categories for organization.

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | Integer (PK) | Auto-generated |
| `name` | CharField(100) | Unique |

### Supplier
Information about product suppliers.

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | Integer (PK) | Auto-generated |
| `name` | CharField(100) | Required |
| `email` | EmailField | Required |
| `phone` | CharField(20) | Required |

### Product
Core inventory product information.

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | Integer (PK) | Auto-generated |
| `name` | CharField(200) | Required |
| `category` | ForeignKey(Category) | Required |
| `supplier` | ForeignKey(Supplier) | Required |
| `price` | DecimalField(10,2) | Required |
| `stock` | Integer | Required |
| `reorder_level` | Integer | Default: 10 |
| `created_at` | DateTimeField | Auto-set (creation) |
| `is_low_stock` | Boolean (property) | Read-only |

### Order
Purchase orders for inventory replenishment.

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | Integer (PK) | Auto-generated |
| `status` | CharField(20) | Choices: 'pending', 'completed' |
| `created_at` | DateTimeField | Auto-set (creation) |

### OrderItem
Individual items within an order.

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | Integer (PK) | Auto-generated |
| `order` | ForeignKey(Order) | Required |
| `product` | ForeignKey(Product) | Required |
| `quantity` | Integer | Required |
| `price` | DecimalField(10,2) | Required |

---

## Authentication

The API uses **JWT (JSON Web Token)** authentication for secure access.

### Obtaining Tokens

**Endpoint**: `POST /api/token/`

**Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-password"
  }'
```

**Response**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refreshing Tokens

**Endpoint**: `POST /api/token/refresh/`

**Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

**Response**:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Using Tokens

Include the access token in the `Authorization` header for all protected endpoints:

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://127.0.0.1:8000/api/products/
```

---

## API Endpoints

All endpoints require JWT authentication (except `/api/token/` for obtaining tokens).

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/token/` | Obtain access and refresh tokens |
| POST | `/api/token/refresh/` | Refresh access token |

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | List all categories |
| POST | `/api/categories/` | Create new category |

### Suppliers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/suppliers/` | List all suppliers |
| POST | `/api/suppliers/` | Create new supplier |

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List all products |
| POST | `/api/products/` | Create new product |
| GET | `/api/products/{id}/` | Retrieve product details |
| PUT | `/api/products/{id}/` | Update product |
| PATCH | `/api/products/{id}/` | Partial product update |
| DELETE | `/api/products/{id}/` | Delete product |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders/` | List all orders |
| POST | `/api/orders/` | Create new order |
| GET | `/api/orders/{id}/` | Retrieve order details |

### Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts/low-stock/` | Get products with low stock |

---

## API Examples

### 1. Authentication - Obtain Token

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response** (200 OK):
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Save the access token for subsequent requests**.

### 2. Categories - Create Category

```bash
curl -X POST http://127.0.0.1:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "Electronics"
  }'
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "Electronics"
}
```

### 3. Categories - List Categories

```bash
curl -X GET http://127.0.0.1:8000/api/categories/ \
  -H "Authorization: Bearer <access_token>"
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Electronics"
  },
  {
    "id": 2,
    "name": "Office Supplies"
  }
]
```

### 4. Suppliers - Create Supplier

```bash
curl -X POST http://127.0.0.1:8000/api/suppliers/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "Acme Electronics",
    "email": "sales@acme.com",
    "phone": "+1-555-123-4567"
  }'
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "Acme Electronics",
  "email": "sales@acme.com",
  "phone": "+1-555-123-4567"
}
```

### 5. Products - Create Product

```bash
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "Wireless Mouse",
    "category_id": 1,
    "supplier_id": 1,
    "price": "29.99",
    "stock": 150,
    "reorder_level": 25
  }'
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "Wireless Mouse",
  "category": {
    "id": 1,
    "name": "Electronics"
  },
  "category_id": 1,
  "supplier": {
    "id": 1,
    "name": "Acme Electronics",
    "email": "sales@acme.com",
    "phone": "+1-555-123-4567"
  },
  "supplier_id": 1,
  "price": "29.99",
  "stock": 150,
  "reorder_level": 25,
  "created_at": "2026-06-13T10:30:00Z",
  "is_low_stock": false
}
```

### 6. Products - List All Products

```bash
curl -X GET http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer <access_token>"
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Wireless Mouse",
    "category": {
      "id": 1,
      "name": "Electronics"
    },
    "supplier": {
      "id": 1,
      "name": "Acme Electronics",
      "email": "sales@acme.com",
      "phone": "+1-555-123-4567"
    },
    "price": "29.99",
    "stock": 150,
    "reorder_level": 25,
    "created_at": "2026-06-13T10:30:00Z",
    "is_low_stock": false
  }
]
```

### 7. Products - Update Product

```bash
curl -X PUT http://127.0.0.1:8000/api/products/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "Wireless Mouse - Updated",
    "category_id": 1,
    "supplier_id": 1,
    "price": "34.99",
    "stock": 100,
    "reorder_level": 20
  }'
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Wireless Mouse - Updated",
  "category": {
    "id": 1,
    "name": "Electronics"
  },
  "category_id": 1,
  "supplier": {
    "id": 1,
    "name": "Acme Electronics",
    "email": "sales@acme.com",
    "phone": "+1-555-123-4567"
  },
  "supplier_id": 1,
  "price": "34.99",
  "stock": 100,
  "reorder_level": 20,
  "created_at": "2026-06-13T10:30:00Z",
  "is_low_stock": false
}
```

### 8. Products - Partial Update (PATCH)

```bash
curl -X PATCH http://127.0.0.1:8000/api/products/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "stock": 80
  }'
```

**Response** (200 OK): Updated product with new stock value.

### 9. Products - Delete Product

```bash
curl -X DELETE http://127.0.0.1:8000/api/products/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Response** (204 No Content): Product deleted successfully.

### 10. Orders - Create Order

```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "status": "pending",
    "items": [
      {
        "product_id": 1,
        "quantity": 10,
        "price": "29.99"
      },
      {
        "product_id": 2,
        "quantity": 5,
        "price": "49.99"
      }
    ]
  }'
```

**Response** (201 Created):
```json
{
  "id": 1,
  "status": "pending",
  "created_at": "2026-06-13T10:35:00Z",
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Wireless Mouse",
        "category": {
          "id": 1,
          "name": "Electronics"
        },
        "supplier": {
          "id": 1,
          "name": "Acme Electronics",
          "email": "sales@acme.com",
          "phone": "+1-555-123-4567"
        },
        "price": "29.99",
        "stock": 140,
        "reorder_level": 25,
        "created_at": "2026-06-13T10:30:00Z",
        "is_low_stock": false
      },
      "product_id": 1,
      "quantity": 10,
      "price": "29.99"
    },
    {
      "id": 2,
      "product": {
        "id": 2,
        "name": "Keyboard",
        "category": {
          "id": 1,
          "name": "Electronics"
        },
        "supplier": {
          "id": 1,
          "name": "Acme Electronics",
          "email": "sales@acme.com",
          "phone": "+1-555-123-4567"
        },
        "price": "49.99",
        "stock": 75,
        "reorder_level": 15,
        "created_at": "2026-06-13T10:31:00Z",
        "is_low_stock": false
      },
      "product_id": 2,
      "quantity": 5,
      "price": "49.99"
    }
  ]
}
```

### 11. Orders - List Orders

```bash
curl -X GET http://127.0.0.1:8000/api/orders/ \
  -H "Authorization: Bearer <access_token>"
```

**Response** (200 OK): List of all orders.

### 12. Orders - Retrieve Order Details

```bash
curl -X GET http://127.0.0.1:8000/api/orders/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Response** (200 OK): Detailed order information.

### 13. Alerts - Get Low Stock Products

```bash
curl -X GET http://127.0.0.1:8000/api/alerts/low-stock/ \
  -H "Authorization: Bearer <access_token>"
```

**Response** (200 OK):
```json
[
  {
    "id": 3,
    "name": "USB Cable",
    "category": {
      "id": 1,
      "name": "Electronics"
    },
    "supplier": {
      "id": 1,
      "name": "Acme Electronics",
      "email": "sales@acme.com",
      "phone": "+1-555-123-4567"
    },
    "price": "5.99",
    "stock": 8,
    "reorder_level": 10,
    "created_at": "2026-06-13T10:32:00Z",
    "is_low_stock": true
  }
]
```

---

## Admin Interface

The Django admin interface provides a graphical interface for managing data.

### Access Admin

1. Start the development server
2. Open http://127.0.0.1:8000/admin/
3. Log in with superuser credentials

### Admin Features

- Create, read, update, and delete all models
- Search and filter by fields
- Bulk actions
- Change logs and history

### Admin Models

The following models are registered in admin:

```python
# From SmeApp/admin.py
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
```

---

## Testing

### Run Tests

```bash
python manage.py test
```

### Run System Checks

```bash
python manage.py check
```

**Output**:
```
System check identified no issues (0 silenced).
```

### Run Specific Test

```bash
python manage.py test SmeApp.tests.CategoryTestCase
```

### Test Coverage

Generate test coverage report:

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

Open `htmlcov/index.html` to view coverage report.

---

## Troubleshooting

### Issue: Connection Refused on PostgreSQL

**Error**: `psycopg2.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed`

**Solution**:
1. Ensure PostgreSQL is installed and running
2. Check connection credentials in `SmeProject/settings.py`
3. Verify database exists: `psql -U postgres -l`
4. If database doesn't exist, create it:
   ```sql
   CREATE DATABASE inventory_db;
   ```

### Issue: ModuleNotFoundError: No module named 'rest_framework'

**Error**: `ModuleNotFoundError: No module named 'rest_framework'`

**Solution**:
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Issue: Migration Errors

**Error**: `django.core.management.base.SystemCheckError`

**Solution**:
```bash
# Check for issues
python manage.py check

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Issue: 401 Unauthorized on API Endpoints

**Error**: `{"detail":"Authentication credentials were not provided."}`

**Solution**:
1. Obtain a token: `POST /api/token/`
2. Include token in header: `Authorization: Bearer <access_token>`
3. Ensure token is not expired (refresh if needed)

### Issue: Port 8000 Already in Use

**Error**: `OSError: [Errno 10048] Only one usage of each socket address`

**Solution**:
```bash
# Use different port
python manage.py runserver 8001
```

Or kill process on port 8000:
```powershell
# PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force

# CMD
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: CSRF Token Missing

**Error**: `Forbidden (403): CSRF verification failed.`

**Solution**:
- POST requests through API should work (DRF handles CSRF)
- If using form-based requests, include CSRF token:
  ```bash
  curl -X POST http://127.0.0.1:8000/api/products/ \
    -H "X-CSRFToken: <csrf_token>"
  ```

### Issue: Database Migration Conflicts

**Error**: `Conflicting migrations detected`

**Solution**:
```bash
# Squash migrations
python manage.py squashmigrations SmeApp

# Revert to initial state (development only!)
python manage.py migrate SmeApp zero
python manage.py migrate
```

---

## Development Notes

### Key Architectural Decisions

1. **JWT Authentication**: Chosen for stateless, scalable API authentication
2. **PostgreSQL Database**: Recommended for production (SQLite for development)
3. **Nested Serializers**: Used for related objects (Category, Supplier in Product)
4. **Select Related**: Applied in views to optimize database queries

### Future Enhancements

- [ ] Add pagination to list endpoints
- [ ] Implement filtering and search
- [ ] Add request/response validation logging
- [ ] Create batch import endpoint for products
- [ ] Implement email notifications for low-stock alerts
- [ ] Add role-based access control (RBAC)
- [ ] Create API rate limiting
- [ ] Add comprehensive unit and integration tests
- [ ] Implement API versioning
- [ ] Add OpenAPI/Swagger documentation

### Database Performance Tips

1. **Use indexes** on frequently queried fields:
   ```python
   class Product(models.Model):
       name = models.CharField(max_length=200, db_index=True)
   ```

2. **Use select_related()** for one-to-one and foreign key:
   ```python
   Product.objects.select_related('category', 'supplier')
   ```

3. **Use prefetch_related()** for many-to-many:
   ```python
   Order.objects.prefetch_related('items__product')
   ```

### Production Deployment Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Update `ALLOWED_HOSTS` with domain
- [ ] Generate strong `SECRET_KEY`
- [ ] Use PostgreSQL database
- [ ] Set up HTTPS/SSL
- [ ] Configure static files serving
- [ ] Set up logging and monitoring
- [ ] Configure email backend
- [ ] Set up automated backups
- [ ] Use environment variables for sensitive data

### Environment Variables (Production)

```bash
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=strong-password
DB_HOST=your-db-host.com
DB_PORT=5432
```

---

## Support & Contributing

For issues, questions, or contributions:

1. Check this README
2. Review the Troubleshooting section
3. Check Django and DRF documentation:
   - [Django Docs](https://docs.djangoproject.com/)
   - [DRF Docs](https://www.django-rest-framework.org/)
   - [SimpleJWT Docs](https://django-rest-framework-simplejwt.readthedocs.io/)

---

## License

This project is part of the SME Inventory Management System initiative.

---

**Last Updated**: June 13, 2026  
**Django Version**: 5.2.12  
**Python Version**: 3.11+  
**Database**: PostgreSQL/SQLite
