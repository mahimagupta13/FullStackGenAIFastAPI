## FastAPICRMLeadTime Usage (CSV-backed)

### Run
```bash
uvicorn FastAPICRMLeadTime.main:app --reload --host 127.0.0.1 --port 8000
```

### CSV Persistence
- Data is loaded from and saved to `customers.csv` automatically.
- To start clean, delete or rename the CSV file before running.

### Quickstart
```bash
curl -X POST http://127.0.0.1:8000/customers -H 'Content-Type: application/json' \
  -d '{"id":1,"name":"Alice","email":"alice@example.com","asked_q":true,"referred":false,"past_touchpoints":2}'
curl http://127.0.0.1:8000/customers
```

### AI Qualification
- Set `GROQ_API_KEY` in environment before starting the server.
```bash
export GROQ_API_KEY=sk_...
uvicorn FastAPICRMLeadTime.main:app --reload
```
```bash
curl -X POST http://127.0.0.1:8000/customers/1/qualify
```

### Streamlit UI
- File: `FastAPICRMLeadTime/ui.py`
- Update `BASE_URL` to point to your running API
```bash
streamlit run FastAPICRMLeadTime/ui.py
```
