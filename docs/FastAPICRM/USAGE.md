## FastAPICRM Usage

### Run
```bash
uvicorn FastAPICRM.main:app --reload --host 127.0.0.1 --port 8000
```

### Quickstart
```bash
curl -X POST http://127.0.0.1:8000/customers -H 'Content-Type: application/json' \
  -d '{"id":1,"name":"Alice","email":"alice@example.com","phone":"","address":""}'
curl http://127.0.0.1:8000/customers
```

### Optional Streamlit UI
- File: `FastAPICRM/ui.py`
- It uses `BASE_URL` constant. Update it to your API base (default points to a hosted demo).
```bash
streamlit run FastAPICRM/ui.py
```
