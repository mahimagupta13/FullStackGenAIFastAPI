## FastAPICRMLeadTimeDB API Reference (Supabase-backed)

- Base URL: http://127.0.0.1:8000
- App module: `FastAPICRMLeadTimeDB/main.py`
- Storage: Supabase table `customers`
- Requires: `SUPABASE_URL`, `SUPABASE_KEY`; optional `GROQ_API_KEY` for AI

### Models
- Customer: id, name, email, phone?, address?, country?, goal?, budget?, webinar_join?, webinar_leave?, asked_q, referred, past_touchpoints, created_at, closed_at, engaged_mins?, score?, reasoning?, status?
- CustomerOut: Customer + lead_time_days

### Endpoints
- POST /customers → CustomerOut (rejects duplicate id)
- GET /customers → CustomerOut[]
- GET /customers/{id} → CustomerOut
- PUT /customers/{id} → CustomerOut
- DELETE /customers/{id} → CustomerOut
- GET /customers/{id}/lead-time → { id, lead_time_days }
- POST /customers/{id}/qualify → CustomerOut (updates Supabase with score fields)
- GET /customers/export/csv → { message, data: [rows...] }
- GET /customers/download/csv → { filename, content_type, content }

### Examples
- Start (env required)
```bash
export SUPABASE_URL=...; export SUPABASE_KEY=...
uvicorn FastAPICRMLeadTimeDB.main:app --reload
```
- Create and list
```bash
curl -s -X POST http://127.0.0.1:8000/customers -H 'Content-Type: application/json' \
  -d '{"id":1,"name":"Alice","email":"alice@example.com"}'
curl -s http://127.0.0.1:8000/customers
```
- Qualify
```bash
export GROQ_API_KEY=sk_...
curl -s -X POST http://127.0.0.1:8000/customers/1/qualify
```

### Configuration
- SUPABASE_URL and SUPABASE_KEY must be set; otherwise endpoints will error
- GROQ_API_KEY required for AI qualification
