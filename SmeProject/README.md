# SME Inventory Management System

This Django project provides an inventory management REST API with JWT authentication.

## Overview

Features:
- Add products, categories, suppliers
- Manage product inventory and reorder levels
- Create and view orders
- Low-stock alert endpoint
- JWT-based authentication for protected API access

## Project Structure

- `manage.py` - Django CLI entry point
- `SmeProject/` - main Django settings and URLs
- `SmeApp/` - inventory app containing models, views, serializers, admin, and URLs
- `Templates/` - optional templates folder

## Requirements

- Python 3.11+ (project uses 3.14 in this workspace)
- Django
- Django REST Framework
- djangorestframework-simplejwt

## Setup

1. Open a terminal in the project root:

```console
cd e:\SME-Inventory-Management-System\SmeProject
```

2. Create and activate a virtual environment if needed:

```console
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:

```console
pip install -r requirements.txt
```

4. Apply database migrations:

```console
.\.venv\Scripts\python.exe manage.py migrate
```

5. Create a superuser for admin access:

```console
.\.venv\Scripts\python.exe manage.py createsuperuser
```

## Run the development server

```console
.\.venv\Scripts\python.exe manage.py runserver
```

Then open `http://127.0.0.1:8000/` or the API endpoints below.

## Authentication

The API uses JWT authentication with these endpoints:

- `POST /api/token/` - obtain access and refresh tokens
- `POST /api/token/refresh/` - refresh access token

Example request to obtain a token:

```json
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

Response:

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

Use the access token in subsequent requests:

```
Authorization: Bearer <access_token>
```

## API Endpoints

### Categories
- `GET /api/categories/`
- `POST /api/categories/`

### Suppliers
- `GET /api/suppliers/`
- `POST /api/suppliers/`

### Products
- `GET /api/products/`
- `POST /api/products/`
- `GET /api/products/{id}/`
- `PUT /api/products/{id}/`
- `DELETE /api/products/{id}/`

### Orders
- `GET /api/orders/`
- `POST /api/orders/`
- `GET /api/orders/{id}/`

### Alerts
- `GET /api/alerts/low-stock/`

## Example API Usage

### Create a category

```bash
curl -X POST http://127.0.0.1:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"name": "Electronics"}'
```

### Create a supplier

```bash
curl -X POST http://127.0.0.1:8000/api/suppliers/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"name": "Acme Supplies", "email": "sales@acme.com", "phone": "123-456-7890"}'
```

### Create a product

```bash
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"name": "Widget", "category_id": 1, "supplier_id": 1, "price": "19.99", "stock": 50, "reorder_level": 10}'
```

### Create an order

```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"status": "pending", "items": [{"product_id": 1, "quantity": 2, "price": "19.99"}]}'
```

### Check low-stock products

```bash
curl -X GET http://127.0.0.1:8000/api/alerts/low-stock/ \
  -H "Authorization: Bearer <access_token>"
```

## Admin site

Open the Django admin interface at:

```
http://127.0.0.1:8000/admin/
```

Use the superuser credentials created earlier.

## Testing

Run system checks and tests with:

```console
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

> Note: The current project includes no automated tests, so `manage.py test` will report `0 tests run`.

## Customization

- To switch to PostgreSQL, update `SmeProject/settings.py` and set `DATABASES` accordingly.
- To expose public endpoints, update view-level permissions or adjust `REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES`.
- To add stock decrement on order creation, modify `OrderSerializer.create()` to update product inventory.

## Notes

- The project is currently configured for development with `DEBUG = True`.
- `SmeApp` contains the inventory models and REST API.
- JWT tokens are returned by `/api/token/` and must be sent in the `Authorization` header.
