## TravelPlanner API Reference

- Base URL: http://localhost:8000
- OpenAPI UIs: http://localhost:8000/docs (Swagger), http://localhost:8000/redoc (ReDoc)
- Auth: Bearer JWT for protected endpoints (see /auth/login)

### Authentication
- POST /auth/register
  - Description: Register a new user
  - Request
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "StrongP@ssw0rd"
}
```
  - Response 200
```json
{ "message": "User registered successfully" }
```

- POST /auth/login
  - Description: Login and receive access token
  - Request
```json
{ "username": "alice", "password": "StrongP@ssw0rd" }
```
  - Response 200
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```
  - Usage: Send header `Authorization: Bearer <jwt>` for protected routes

### Destinations
- GET /destinations
  - Returns: List of Destination
```json
[{"destination_id":1,"name":"Paris","country":"France","description":"...","image_url":"...","climate":"Temperate","best_time_to_visit":"Apr-Jun"}]
```

- GET /destinations/{destination_id}
  - Returns: Destination or 404

### Hotels
- GET /hotels
  - Query: `destination_id` (optional)
  - Returns: List of Hotel

### Activities
- GET /activities
  - Query: `destination_id` (optional)
  - Returns: List of Activity

### Itineraries (Auth required)
- GET /itineraries
  - Header: `Authorization: Bearer <jwt>`
  - Returns: List of Itinerary for current user

- POST /itineraries
  - Header: `Authorization: Bearer <jwt>`
  - Request (ItineraryCreate)
```json
{
  "name": "Rome Trip",
  "start_date": "2025-10-10",
  "end_date": "2025-10-14",
  "details_json": {"days":[{"day":1,"activities":["Colosseum","Roman Forum"]}]}
}
```
  - Response 200
```json
{ "message": "Itinerary created successfully" }
```

### Reviews (POST requires Auth)
- GET /reviews
  - Query: `destination_id` (optional)
  - Returns: List of Review

- POST /reviews
  - Header: `Authorization: Bearer <jwt>`
  - Request (ReviewCreate)
```json
{ "destination_id": 1, "rating": 5, "comment": "Amazing!" }
```
  - Response 200
```json
{ "message": "Review created successfully" }
```

### AI
- POST /recommendations
  - Description: AI-powered travel tips; falls back to mock text if Groq is not configured
  - Request (RecommendationRequest)
```json
{
  "destination_id": 1,
  "budget": 1500,
  "duration": 5,
  "interests": ["Food","History"],
  "travel_style": "Mid-range"
}
```
  - Response 200
```json
{ "recommendations": "...markdown/plaintext content..." }
```

- POST /itinerary/generate
  - Description: Generate a complete itinerary using AI; returns text/JSON content
  - Request: Same shape as RecommendationRequest
  - Response 200
```json
{ "itinerary": "...markdown/JSON content..." }
```

### Health
- GET /health
  - Returns current status and timestamp

### Models
- UserCreate: { username: string, email: string, password: string }
- UserLogin: { username: string, password: string }
- User: { user_id, username, email, role, created_at }
- Destination: { destination_id, name, country, description, image_url, climate, best_time_to_visit }
- Hotel: { hotel_id, destination_id, name, price_per_night, rating, availability, amenities }
- Activity: { activity_id, destination_id, name, category, price, rating, duration, description }
- ItineraryCreate: { name, start_date, end_date, details_json<object> }
- Itinerary: { itinerary_id, user_id, name, start_date, end_date, details_json<object>, created_at }
- ReviewCreate: { destination_id, rating, comment }
- Review: { review_id, user_id, destination_id, rating, comment, created_at }
- RecommendationRequest: { destination_id?, budget?, duration?, interests?, travel_style? }

### Examples
- Login and fetch itineraries
```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"StrongP@ssw0rd"}' | jq -r .access_token
```
```bash
TOKEN=... # from previous command
curl -s http://localhost:8000/itineraries -H "Authorization: Bearer $TOKEN"
```

- Create itinerary
```bash
curl -s -X POST http://localhost:8000/itineraries \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Rome Trip","start_date":"2025-10-10","end_date":"2025-10-14","details_json":{"days":[{"day":1,"activities":["Colosseum"]}]}}'
```

- Get recommendations
```bash
curl -s -X POST http://localhost:8000/recommendations \
  -H 'Content-Type: application/json' \
  -d '{"destination_id":1,"budget":1500,"duration":5,"interests":["Food"],"travel_style":"Mid-range"}'
```

### Configuration
- Environment variables (see `TravelPlanner/config.py`):
  - GROQ_API_KEY: Groq key (optional; mock output is used if not set)
  - SECRET_KEY: JWT signing secret
  - ALGORITHM: JWT algorithm (HS256)
- CSV data files under `TravelPlanner/data/`
