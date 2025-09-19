import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# File paths
DATA_DIR = "data"
USERS_FILE = f"{DATA_DIR}/users.csv"
DESTINATIONS_FILE = f"{DATA_DIR}/destinations.csv"
HOTELS_FILE = f"{DATA_DIR}/hotels.csv"
ACTIVITIES_FILE = f"{DATA_DIR}/activities.csv"
ITINERARIES_FILE = f"{DATA_DIR}/itineraries.csv"
REVIEWS_FILE = f"{DATA_DIR}/reviews.csv"
ANALYTICS_FILE = f"{DATA_DIR}/analytics.csv"
