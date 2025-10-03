## FastAPICRM API Reference (In-Memory)

- Base URL: http://127.0.0.1:8000
- App module: `FastAPICRM/main.py`

### Model
- Customer
```json
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "phone": "123456",
  "address": "NYC"
}
```

### Endpoints
- POST /customers
  - Create a customer
  - Request: Customer
  - Response 200: Customer

- GET /customers
  - List all customers
  - Response 200: Customer[]

- PUT /customers/{id}
  - Replace customer by id
  - Request: Customer
  - Response 200: Customer or 404

- DELETE /customers/{id}
  - Delete by id
  - Response 200: Customer or 404

### Examples
- Start the API
```bash
uvicorn FastAPICRM.main:app --reload
```
- Create and list
```bash
curl -s -X POST http://127.0.0.1:8000/customers -H 'Content-Type: application/json' \
  -d '{"id":1,"name":"Alice","email":"alice@example.com"}'
curl -s http://127.0.0.1:8000/customers
```
