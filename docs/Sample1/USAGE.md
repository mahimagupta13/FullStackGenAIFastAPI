## Sample1 Usage (Arithmetic)

### Run
```bash
uvicorn Sample1.api:app --reload --host 127.0.0.1 --port 8000
```

### cURL Examples
```bash
curl -s -X POST http://127.0.0.1:8000/add -H 'Content-Type: application/json' -d '{"x":2,"y":3}'
curl -s -X POST http://127.0.0.1:8000/divide -H 'Content-Type: application/json' -d '{"x":6,"y":0}'
```

### Frontend
Open `Sample1/frontend/index.html` in a browser and interact with the UI. Update fetch URL if running on a different host/port.
