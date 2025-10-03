## Sample1 API Reference (Arithmetic)

- Backend modules: `Sample1/api.py` (float), `Sample1/api copy.py` (int)
- Base URL: http://127.0.0.1:8000

### Model
- Numbers: { x: number, y: number }

### Endpoints (api.py)
- POST /add → { result: number }
- POST /subtract → { result: number }
- POST /multiply → { result: number }
- POST /divide → { result: number | error }

### Endpoints (api copy.py)
- POST /add → { result: int }
- POST /multiply → { result: int }
- POST /del → { result: int }
- POST /div → { result: number }

### Examples
```bash
uvicorn Sample1.api:app --reload
curl -s -X POST http://127.0.0.1:8000/add -H 'Content-Type: application/json' -d '{"x":3,"y":5}'
```

### Frontend
- File: `Sample1/frontend/index.html`
- Expects backend at `http://127.0.0.1:8000`
