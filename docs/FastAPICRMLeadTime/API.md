## FastAPICRMLeadTime API Reference (CSV-backed)

- Base URL: http://127.0.0.1:8000
- App module: `FastAPICRMLeadTime/main.py`
- Storage: CSV file `customers.csv` in working directory
- Optional AI: requires `GROQ_API_KEY`

### Models
- Customer: fields include id, name, email, phone?, address?, country?, goal?, budget?, webinar_join?, webinar_leave?, asked_q, referred, past_touchpoints, created_at, closed_at, engaged_mins?, score?, reasoning?, status?
- CustomerOut: Customer + lead_time_days

### Endpoints
- POST /customers → CustomerOut
- GET /customers → CustomerOut[]
- GET /customers/{id} → CustomerOut
- PUT /customers/{id} → CustomerOut
- DELETE /customers/{id} → CustomerOut
- GET /customers/{id}/lead-time → { id, lead_time_days }
- POST /customers/{id}/qualify → CustomerOut (invokes Groq; set GROQ_API_KEY)
- GET /customers/export/csv → { message, data: [rows...] }
- GET /customers/download/csv → { message, file_path }

### Examples
- Start
```bash
uvicorn FastAPICRMLeadTime.main:app --reload
```
- Create
```bash
curl -s -X POST http://127.0.0.1:8000/customers -H 'Content-Type: application/json' \
  -d '{"id":1,"name":"Alice","email":"alice@example.com","asked_q":true,"referred":false,"past_touchpoints":2}'
```
- Qualify (requires GROQ_API_KEY)
```bash
curl -s -X POST http://127.0.0.1:8000/customers/1/qualify
```
- Lead time
```bash
curl -s http://127.0.0.1:8000/customers/1/lead-time
```

### Configuration
- Environment: `GROQ_API_KEY` for AI scoring
- CSV is written by the service; ensure write permission
