# Quick Start Guide - Order Management API

This guide will get you up and running with the Order Management API in 5 minutes.

## Prerequisites

- Python 3.11+
- Docker Desktop (or Docker + Docker Compose)

## Step 1: Start the Database

```bash
# Navigate to backend directory
cd backend

# Start PostgreSQL and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
```

You should see:
```
NAME                        STATUS    PORTS
order_management_db        Up         0.0.0.0:5432->5432/tcp
order_management_redis     Up         0.0.0.0:6379->6379/tcp
```

## Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -e ".[dev]"
```

## Step 3: Run the API

```bash
# Start the API server
uvicorn src.interfaces.http.app:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Step 4: Test the API

Open your browser and visit:

- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Step 5: Try the API

### Create an Order

```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123e4567-e89b-12d3-a456-426614174000",
    "shipping_address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94102",
      "country": "US"
    }
  }'
```

Response:
```json
{
  "id": "abc12345-...",
  "customer_id": "123e4567-...",
  "status": "DRAFT",
  "total": 0.00,
  "currency": "USD",
  "created_at": "2026-01-14T12:00:00"
}
```

### Add a Product

Replace `{order_id}` with the ID from the previous response:

```bash
curl -X POST http://localhost:8000/api/orders/{order_id}/items \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "223e4567-e89b-12d3-a456-426614174001",
    "quantity": 2,
    "unit_price": 29.99,
    "currency": "USD"
  }'
```

### Get Order Details

```bash
curl http://localhost:8000/api/orders/{order_id}
```

## Complete Order Workflow

Here's a complete example workflow:

```bash
# 1. Create order
ORDER_ID=$(curl -s -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123e4567-e89b-12d3-a456-426614174000",
    "shipping_address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94102",
      "country": "US"
    }
  }' | jq -r '.id')

echo "Created order: $ORDER_ID"

# 2. Add items
curl -X POST http://localhost:8000/api/orders/$ORDER_ID/items \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "223e4567-e89b-12d3-a456-426614174001",
    "quantity": 2,
    "unit_price": 29.99,
    "currency": "USD"
  }'

# 3. Submit order
curl -X POST http://localhost:8000/api/orders/$ORDER_ID/submit

# 4. Confirm payment
curl -X POST http://localhost:8000/api/orders/$ORDER_ID/payment \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "pay_123456",
    "amount_paid": 59.98,
    "currency": "USD"
  }'

# 5. Ship order
curl -X POST http://localhost:8000/api/orders/$ORDER_ID/ship \
  -H "Content-Type: application/json" \
  -d '{
    "tracking_number": "TRACK123456",
    "carrier": "UPS"
  }'

# 6. Get final order status
curl http://localhost:8000/api/orders/$ORDER_ID | jq
```

## Troubleshooting

### Database connection error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: Make sure PostgreSQL is running:
```bash
docker-compose up -d postgres
docker-compose logs postgres
```

### Port already in use

```
ERROR: address already in use
```

**Solution**: Change the port:
```bash
uvicorn src.interfaces.http.app:app --port 8001
```

### Import errors

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**: Install dependencies:
```bash
pip install -e ".[dev]"
```

## Next Steps

- Read the full [README.md](README.md) for architecture details
- Explore the [Swagger UI](http://localhost:8000/docs) for all endpoints
- Check out the [Domain Model](src/domain/order/) to understand business logic
- Run tests: `pytest tests/unit/ -v`

## Stopping the Services

```bash
# Stop API (Ctrl+C in terminal)

# Stop database
docker-compose down

# Remove data (WARNING: deletes all orders!)
docker-compose down -v
```

---

**Questions?** Check the main README or the code comments for more details!
