## FastAPICRMLeadTimeDB Usage (Supabase-backed)

### Run
```bash
export SUPABASE_URL=...; export SUPABASE_KEY=...
uvicorn FastAPICRMLeadTimeDB.main:app --reload --host 127.0.0.1 --port 8000
```

### Quickstart
```bash
curl -X POST http://127.0.0.1:8000/customers -H 'Content-Type: application/json' \
  -d '{"id":1,"name":"Alice","email":"alice@example.com"}'
curl http://127.0.0.1:8000/customers
```

### AI Qualification
```bash
export GROQ_API_KEY=sk_...
curl -X POST http://127.0.0.1:8000/customers/1/qualify
```

### Streamlit UI
- File: `FastAPICRMLeadTimeDB/ui.py`
- Update `BASE_URL` to point to your API
```bash
streamlit run FastAPICRMLeadTimeDB/ui.py
```
