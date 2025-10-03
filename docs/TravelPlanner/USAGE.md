## TravelPlanner Usage Guide

### Prerequisites
- Python 3.9+
- `pip install -r TravelPlanner/requirements.txt`
- `.env` file in `TravelPlanner/`:
```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_here
```

### Run
- Backend
```bash
cd TravelPlanner
python start_backend.py
# API at http://localhost:8000
```
- Frontend (new terminal)
```bash
cd TravelPlanner
python start_frontend.py
# UI at http://localhost:8501
```

### Auth Quickstart
```bash
curl -X POST http://localhost:8000/auth/register -H 'Content-Type: application/json' \
  -d '{"username":"alice","email":"alice@example.com","password":"StrongP@ssw0rd"}'
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"StrongP@ssw0rd"}' | jq -r .access_token)
```

### Typical Flows
- Browse public data: `/destinations`, `/hotels?destination_id=...`, `/activities?destination_id=...`
- Create itinerary (needs auth): `/itineraries`
- Write review (needs auth): `/reviews`
- Ask AI for recommendations: `/recommendations`
- Generate AI itinerary: `/itinerary/generate`

### Frontend Tips
- Configure backend URL in `TravelPlanner/UI.py` via `API_BASE_URL`
- Use the sidebar for auth; tabs expose Destinations, Itineraries, AI, Reviews

### Data Storage
- CSV files are under `TravelPlanner/data` and are created on demand
- Ensure the process has write permission to this folder

### Troubleshooting
- Cannot connect: ensure backend is running and CORS allows your origin
- Auth 401: supply `Authorization: Bearer <token>` header
- AI endpoints return demo text: set a valid `GROQ_API_KEY` and restart
