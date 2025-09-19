# 🧳 Travel Planner App

A full-stack travel planning application built with Python FastAPI backend and Streamlit frontend, featuring AI-powered recommendations using Groq LLM.

## ✨ Features

- **User Authentication**: Register, login, and manage user accounts
- **Destination Management**: Browse destinations with detailed information
- **AI-Powered Recommendations**: Get personalized travel suggestions using Groq LLM
- **Itinerary Creation**: Create, edit, and manage travel itineraries
- **Review System**: Rate and review destinations
- **Data Export**: Export itineraries to CSV format
- **Admin Dashboard**: Manage destinations, hotels, and activities
- **CSV Data Storage**: Lightweight file-based data storage

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit (Python)
- **LLM**: Groq API
- **Data Storage**: CSV files
- **Authentication**: JWT tokens

## 📁 Project Structure

```
TravelPlanner/
├── main.py                 # FastAPI backend
├── UI.py                   # Streamlit frontend
├── config.py              # Configuration settings
├── requirements.txt        # Python dependencies
├── start_backend.py       # Backend startup script
├── start_frontend.py      # Frontend startup script
├── data/                  # CSV data files
│   ├── users.csv
│   ├── destinations.csv
│   ├── hotels.csv
│   ├── activities.csv
│   ├── itineraries.csv
│   ├── reviews.csv
│   └── analytics.csv
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TravelPlanner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

4. **Start the backend**
   ```bash
   python start_backend.py
   ```
   The API will be available at: http://localhost:8000

5. **Start the frontend** (in a new terminal)
   ```bash
   python start_frontend.py
   ```
   The UI will be available at: http://localhost:8501

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Destinations
- `GET /destinations` - Get all destinations
- `GET /destinations/{id}` - Get destination by ID

### Hotels
- `GET /hotels` - Get all hotels
- `GET /hotels?destination_id={id}` - Get hotels by destination

### Activities
- `GET /activities` - Get all activities
- `GET /activities?destination_id={id}` - Get activities by destination

### Itineraries
- `GET /itineraries` - Get user itineraries (requires auth)
- `POST /itineraries` - Create new itinerary (requires auth)

### Reviews
- `GET /reviews` - Get all reviews
- `POST /reviews` - Create new review (requires auth)

### AI Recommendations
- `POST /recommendations` - Get AI recommendations
- `POST /itinerary/generate` - Generate complete itinerary

## 🤖 AI Features

The application uses Groq's LLM to provide:

1. **Personalized Recommendations**: Based on user preferences, budget, and interests
2. **Itinerary Generation**: Complete day-by-day travel plans
3. **Travel Insights**: AI-generated insights and tips
4. **Smart Suggestions**: Context-aware recommendations

## 📊 Data Models

### Users
- User authentication and role management
- Password hashing with bcrypt

### Destinations
- Name, country, description
- Climate and best time to visit
- Image URLs

### Hotels
- Name, price, rating, amenities
- Linked to destinations

### Activities
- Name, category, price, rating
- Duration and description
- Linked to destinations

### Itineraries
- User-specific travel plans
- JSON format for flexible day-by-day details

### Reviews
- User ratings and comments
- Linked to destinations

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- CORS enabled for frontend integration

## 📈 Usage

1. **Register/Login**: Create an account or login
2. **Browse Destinations**: Explore available destinations
3. **Get Recommendations**: Use AI to get personalized suggestions
4. **Create Itineraries**: Plan your trips with detailed schedules
5. **Write Reviews**: Share your travel experiences
6. **Export Data**: Download your itineraries as CSV

## 🛠️ Development

### Running in Development Mode

Backend with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend with auto-reload:
```bash
streamlit run UI.py --server.port 8501
```

### API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🚀 Deployment

### Backend Deployment
1. Set environment variables
2. Install dependencies
3. Run with production WSGI server (e.g., Gunicorn)

### Frontend Deployment
1. Deploy to Streamlit Cloud
2. Or use Docker for containerized deployment

## 📝 Sample Data

The application comes with sample data including:
- 8 popular destinations
- 10 hotels across different price ranges
- 20 activities in various categories
- Sample itineraries and reviews

## 🔧 Configuration

Key configuration options in `config.py`:
- API keys and secrets
- File paths for CSV storage
- JWT settings
- CORS configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation
2. Review the logs for error messages
3. Ensure all dependencies are installed
4. Verify environment variables are set correctly

## 🔮 Future Enhancements

- Real-time booking integration
- Mobile app development
- Advanced analytics dashboard
- Multi-language support
- Social features and sharing
- Offline mode support
