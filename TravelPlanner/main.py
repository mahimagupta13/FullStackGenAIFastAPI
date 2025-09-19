from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import json
import hashlib
import secrets
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import os
try:
    from groq import Groq
except ImportError:
    Groq = None
import config

# Initialize FastAPI app
app = FastAPI(title="Travel Planner API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Groq client will be initialized when needed

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    created_at: str

class Destination(BaseModel):
    destination_id: int
    name: str
    country: str
    description: str
    image_url: str
    climate: str
    best_time_to_visit: str

class Hotel(BaseModel):
    hotel_id: int
    destination_id: int
    name: str
    price_per_night: int
    rating: int
    availability: str
    amenities: str

class Activity(BaseModel):
    activity_id: int
    destination_id: int
    name: str
    category: str
    price: int
    rating: int
    duration: int
    description: str

class ItineraryCreate(BaseModel):
    name: str
    start_date: str
    end_date: str
    details_json: Dict[str, Any]

class Itinerary(BaseModel):
    itinerary_id: int
    user_id: int
    name: str
    start_date: str
    end_date: str
    details_json: Dict[str, Any]
    created_at: str

class ReviewCreate(BaseModel):
    destination_id: int
    rating: int
    comment: str

class Review(BaseModel):
    review_id: int
    user_id: int
    destination_id: int
    rating: int
    comment: str
    created_at: str

class RecommendationRequest(BaseModel):
    destination_id: Optional[int] = None
    budget: Optional[int] = None
    duration: Optional[int] = None
    interests: Optional[List[str]] = None
    travel_style: Optional[str] = None

# Utility functions
def load_csv(file_path: str) -> pd.DataFrame:
    """Load CSV file and return DataFrame"""
    if not os.path.exists(file_path):
        return pd.DataFrame()
    return pd.read_csv(file_path)

def save_csv(df: pd.DataFrame, file_path: str):
    """Save DataFrame to CSV file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    users_df = load_csv(config.USERS_FILE)
    user_data = users_df[users_df['username'] == username]
    if user_data.empty:
        raise HTTPException(status_code=401, detail="User not found")
    
    user = user_data.iloc[0]
    return User(
        user_id=user['user_id'],
        username=user['username'],
        email=user['email'],
        role=user['role'],
        created_at=user['created_at']
    )

def get_groq_recommendations(prompt: str) -> str:
    """Get recommendations from Groq LLM"""
    try:
        # Check if Groq is available
        if Groq is None:
            return get_mock_recommendations(prompt)
        
        # Initialize Groq client when needed
        if config.GROQ_API_KEY == "your_groq_api_key_here":
            return get_mock_recommendations(prompt)
        
        groq_client = Groq(api_key=config.GROQ_API_KEY)
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=1000
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return get_mock_recommendations(prompt)

def get_mock_recommendations(prompt: str) -> str:
    """Fallback mock recommendations when Groq is not available"""
    return """
    🤖 AI Travel Recommendations (Demo Mode)
    
    Based on your preferences, here are some personalized recommendations:
    
    📍 **Top Destinations:**
    - Paris, France - Perfect for culture and food lovers
    - Tokyo, Japan - Great for adventure and unique experiences
    - Rome, Italy - Ideal for history enthusiasts
    
    🏨 **Hotel Suggestions:**
    - Budget: Look for 3-star hotels in city centers
    - Mid-range: 4-star hotels with good amenities
    - Luxury: 5-star hotels with premium services
    
    🎯 **Activities:**
    - Visit iconic landmarks and museums
    - Try local cuisine and restaurants
    - Explore neighborhoods and local culture
    - Take guided tours for better insights
    
    💡 **Travel Tips:**
    - Book accommodations in advance
    - Research local customs and etiquette
    - Keep copies of important documents
    - Have a flexible itinerary for spontaneous discoveries
    
    Note: Set up your GROQ_API_KEY in the .env file for real AI recommendations!
    """

# Authentication endpoints
@app.post("/auth/register", response_model=Dict[str, str])
async def register(user: UserCreate):
    """Register a new user"""
    users_df = load_csv(config.USERS_FILE)
    
    # Check if user already exists
    if not users_df.empty and (user.username in users_df['username'].values or user.email in users_df['email'].values):
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Create new user
    new_user_id = users_df['user_id'].max() + 1 if not users_df.empty else 1
    hashed_password = hash_password(user.password)
    
    new_user = pd.DataFrame([{
        'user_id': new_user_id,
        'username': user.username,
        'email': user.email,
        'password': hashed_password,
        'role': 'user',
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }])
    
    if users_df.empty:
        save_csv(new_user, config.USERS_FILE)
    else:
        save_csv(pd.concat([users_df, new_user], ignore_index=True), config.USERS_FILE)
    
    return {"message": "User registered successfully"}

@app.post("/auth/login", response_model=Dict[str, str])
async def login(user: UserLogin):
    """Login user and return access token"""
    users_df = load_csv(config.USERS_FILE)
    user_data = users_df[users_df['username'] == user.username]
    
    if user_data.empty or not verify_password(user.password, user_data.iloc[0]['password']):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Destination endpoints
@app.get("/destinations", response_model=List[Destination])
async def get_destinations():
    """Get all destinations"""
    destinations_df = load_csv(config.DESTINATIONS_FILE)
    if destinations_df.empty:
        return []
    
    return [Destination(**row) for _, row in destinations_df.iterrows()]

@app.get("/destinations/{destination_id}", response_model=Destination)
async def get_destination(destination_id: int):
    """Get destination by ID"""
    destinations_df = load_csv(config.DESTINATIONS_FILE)
    destination = destinations_df[destinations_df['destination_id'] == destination_id]
    
    if destination.empty:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    return Destination(**destination.iloc[0])

# Hotel endpoints
@app.get("/hotels", response_model=List[Hotel])
async def get_hotels(destination_id: Optional[int] = None):
    """Get hotels, optionally filtered by destination"""
    hotels_df = load_csv(config.HOTELS_FILE)
    if hotels_df.empty:
        return []
    
    if destination_id:
        hotels_df = hotels_df[hotels_df['destination_id'] == destination_id]
    
    return [Hotel(**row) for _, row in hotels_df.iterrows()]

# Activity endpoints
@app.get("/activities", response_model=List[Activity])
async def get_activities(destination_id: Optional[int] = None):
    """Get activities, optionally filtered by destination"""
    activities_df = load_csv(config.ACTIVITIES_FILE)
    if activities_df.empty:
        return []
    
    if destination_id:
        activities_df = activities_df[activities_df['destination_id'] == destination_id]
    
    return [Activity(**row) for _, row in activities_df.iterrows()]

# Itinerary endpoints
@app.get("/itineraries", response_model=List[Itinerary])
async def get_itineraries(current_user: User = Depends(get_current_user)):
    """Get user's itineraries"""
    itineraries_df = load_csv(config.ITINERARIES_FILE)
    if itineraries_df.empty:
        return []
    
    user_itineraries = itineraries_df[itineraries_df['user_id'] == current_user.user_id]
    if user_itineraries.empty:
        return []
    
    itineraries = []
    for _, row in user_itineraries.iterrows():
        itinerary = Itinerary(
            itinerary_id=row['itinerary_id'],
            user_id=row['user_id'],
            name=row['name'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            details_json=json.loads(row['details_json']),
            created_at=row['created_at']
        )
        itineraries.append(itinerary)
    
    return itineraries

@app.post("/itineraries", response_model=Dict[str, str])
async def create_itinerary(itinerary: ItineraryCreate, current_user: User = Depends(get_current_user)):
    """Create a new itinerary"""
    itineraries_df = load_csv(config.ITINERARIES_FILE)
    
    new_itinerary_id = itineraries_df['itinerary_id'].max() + 1 if not itineraries_df.empty else 1
    
    new_itinerary = pd.DataFrame([{
        'itinerary_id': new_itinerary_id,
        'user_id': current_user.user_id,
        'name': itinerary.name,
        'start_date': itinerary.start_date,
        'end_date': itinerary.end_date,
        'details_json': json.dumps(itinerary.details_json),
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }])
    
    if itineraries_df.empty:
        save_csv(new_itinerary, config.ITINERARIES_FILE)
    else:
        save_csv(pd.concat([itineraries_df, new_itinerary], ignore_index=True), config.ITINERARIES_FILE)
    
    return {"message": "Itinerary created successfully"}

# Review endpoints
@app.get("/reviews", response_model=List[Review])
async def get_reviews(destination_id: Optional[int] = None):
    """Get reviews, optionally filtered by destination"""
    reviews_df = load_csv(config.REVIEWS_FILE)
    if reviews_df.empty:
        return []
    
    if destination_id:
        reviews_df = reviews_df[reviews_df['destination_id'] == destination_id]
    
    return [Review(**row) for _, row in reviews_df.iterrows()]

@app.post("/reviews", response_model=Dict[str, str])
async def create_review(review: ReviewCreate, current_user: User = Depends(get_current_user)):
    """Create a new review"""
    reviews_df = load_csv(config.REVIEWS_FILE)
    
    new_review_id = reviews_df['review_id'].max() + 1 if not reviews_df.empty else 1
    
    new_review = pd.DataFrame([{
        'review_id': new_review_id,
        'user_id': current_user.user_id,
        'destination_id': review.destination_id,
        'rating': review.rating,
        'comment': review.comment,
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }])
    
    if reviews_df.empty:
        save_csv(new_review, config.REVIEWS_FILE)
    else:
        save_csv(pd.concat([reviews_df, new_review], ignore_index=True), config.REVIEWS_FILE)
    
    return {"message": "Review created successfully"}

# Recommendation endpoints
@app.post("/recommendations", response_model=Dict[str, str])
async def get_recommendations(request: RecommendationRequest):
    """Get AI-powered travel recommendations"""
    # Load data
    destinations_df = load_csv(config.DESTINATIONS_FILE)
    hotels_df = load_csv(config.HOTELS_FILE)
    activities_df = load_csv(config.ACTIVITIES_FILE)
    reviews_df = load_csv(config.REVIEWS_FILE)
    
    # Build context for LLM
    context = f"""
    Travel Planning Data:
    
    Destinations: {destinations_df.to_dict('records')[:5]}
    Hotels: {hotels_df.to_dict('records')[:10]}
    Activities: {activities_df.to_dict('records')[:15]}
    Reviews: {reviews_df.to_dict('records')[:5]}
    
    User Request:
    - Destination ID: {request.destination_id}
    - Budget: {request.budget}
    - Duration: {request.duration} days
    - Interests: {request.interests}
    - Travel Style: {request.travel_style}
    
    Please provide personalized travel recommendations including:
    1. Recommended destinations
    2. Hotel suggestions within budget
    3. Activities based on interests
    4. Sample itinerary
    5. Travel tips
    """
    
    recommendations = get_groq_recommendations(context)
    
    # Save to analytics
    analytics_df = load_csv(config.ANALYTICS_FILE)
    new_analytics_id = analytics_df['analytics_id'].max() + 1 if not analytics_df.empty else 1
    
    new_analytics = pd.DataFrame([{
        'analytics_id': new_analytics_id,
        'type': 'recommendation',
        'entity_id': request.destination_id or 0,
        'insight_text': recommendations,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }])
    
    if analytics_df.empty:
        save_csv(new_analytics, config.ANALYTICS_FILE)
    else:
        save_csv(pd.concat([analytics_df, new_analytics], ignore_index=True), config.ANALYTICS_FILE)
    
    return {"recommendations": recommendations}

@app.post("/itinerary/generate", response_model=Dict[str, str])
async def generate_itinerary(request: RecommendationRequest):
    """Generate a complete itinerary using AI"""
    # Load data
    destinations_df = load_csv(config.DESTINATIONS_FILE)
    hotels_df = load_csv(config.HOTELS_FILE)
    activities_df = load_csv(config.ACTIVITIES_FILE)
    
    # Get destination info
    destination_info = ""
    if request.destination_id:
        dest = destinations_df[destinations_df['destination_id'] == request.destination_id]
        if not dest.empty:
            destination_info = f"Destination: {dest.iloc[0]['name']}, {dest.iloc[0]['country']}"
    
    # Build prompt for itinerary generation
    prompt = f"""
    Generate a detailed travel itinerary with the following requirements:
    
    {destination_info}
    Duration: {request.duration} days
    Budget: ${request.budget}
    Interests: {request.interests}
    Travel Style: {request.travel_style}
    
    Available data:
    Destinations: {destinations_df.to_dict('records')}
    Hotels: {hotels_df.to_dict('records')}
    Activities: {activities_df.to_dict('records')}
    
    Please provide:
    1. Day-by-day itinerary
    2. Hotel recommendations
    3. Activity suggestions
    4. Budget breakdown
    5. Travel tips
    6. Return the response in JSON format suitable for the itinerary details_json field
    """
    
    itinerary = get_groq_recommendations(prompt)
    
    return {"itinerary": itinerary}

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
