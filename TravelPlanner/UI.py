import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta

# Optional plotly imports
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not available. Some visualizations will be disabled.")

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def make_api_request(endpoint, method="GET", data=None, token=None):
    """Make API request with error handling"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API. Please make sure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def login_user(username, password):
    """Login user and store token in session state"""
    data = {"username": username, "password": password}
    response = make_api_request("/auth/login", method="POST", data=data)
    
    if response and "access_token" in response:
        st.session_state.token = response["access_token"]
        st.session_state.logged_in = True
        st.session_state.username = username
        return True
    return False

def register_user(username, email, password):
    """Register new user"""
    data = {"username": username, "email": email, "password": password}
    response = make_api_request("/auth/register", method="POST", data=data)
    return response is not None

def logout_user():
    """Logout user and clear session state"""
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.username = None

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

# Main app
def main():
    st.markdown('<h1 class="main-header">✈️ Travel Planner</h1>', unsafe_allow_html=True)
    
    # Sidebar for authentication
    with st.sidebar:
        st.markdown("## 🔐 Authentication")
        
        if not st.session_state.logged_in:
            # Login form
            with st.form("login_form"):
                st.markdown("### Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_clicked = st.form_submit_button("Login")
                
                if login_clicked:
                    if login_user(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Login failed!")
            
            st.markdown("---")
            
            # Registration form
            with st.form("register_form"):
                st.markdown("### Register")
                reg_username = st.text_input("Username", key="reg_username")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                register_clicked = st.form_submit_button("Register")
                
                if register_clicked:
                    if register_user(reg_username, reg_email, reg_password):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Registration failed!")
        else:
            st.success(f"Welcome, {st.session_state.username}!")
            if st.button("Logout"):
                logout_user()
                st.rerun()
    
    # Main content based on login status
    if not st.session_state.logged_in:
        st.markdown("""
        <div class="card">
            <h2>Welcome to Travel Planner!</h2>
            <p>Please login or register to access all features:</p>
            <ul>
                <li>Browse destinations and activities</li>
                <li>Create personalized itineraries</li>
                <li>Get AI-powered recommendations</li>
                <li>Read and write reviews</li>
                <li>Export your travel plans</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Show some destinations for non-logged in users
        st.markdown('<h2 class="section-header">🌍 Popular Destinations</h2>', unsafe_allow_html=True)
        destinations = make_api_request("/destinations")
        if destinations:
            cols = st.columns(3)
            for i, dest in enumerate(destinations[:6]):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="card">
                        <h3>{dest['name']}</h3>
                        <p><strong>Country:</strong> {dest['country']}</p>
                        <p>{dest['description'][:100]}...</p>
                        <p><strong>Best time:</strong> {dest['best_time_to_visit']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        # Main dashboard for logged-in users
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dashboard", "🌍 Destinations", "📅 Itineraries", "🤖 AI Recommendations", "⭐ Reviews"])
        
        with tab1:
            st.markdown('<h2 class="section-header">Dashboard</h2>', unsafe_allow_html=True)
            
            # Quick stats
            col1, col2, col3, col4 = st.columns(4)
            
            destinations = make_api_request("/destinations")
            itineraries = make_api_request("/itineraries", token=st.session_state.token)
            reviews = make_api_request("/reviews")
            
            with col1:
                st.metric("Total Destinations", len(destinations) if destinations else 0)
            with col2:
                st.metric("My Itineraries", len(itineraries) if itineraries else 0)
            with col3:
                st.metric("Total Reviews", len(reviews) if reviews else 0)
            with col4:
                st.metric("Active Users", "1")  # Placeholder
            
            # Recent itineraries
            if itineraries:
                st.markdown('<h3 class="section-header">Recent Itineraries</h3>', unsafe_allow_html=True)
                for itinerary in itineraries[-3:]:
                    st.markdown(f"""
                    <div class="card">
                        <h4>{itinerary['name']}</h4>
                        <p><strong>Dates:</strong> {itinerary['start_date']} to {itinerary['end_date']}</p>
                        <p><strong>Created:</strong> {itinerary['created_at']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<h2 class="section-header">Destinations</h2>', unsafe_allow_html=True)
            
            # Search and filter
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("Search destinations", placeholder="Enter city or country name")
            with col2:
                country_filter = st.selectbox("Filter by country", ["All"] + list(set([d['country'] for d in destinations])) if destinations else ["All"])
            
            # Display destinations
            if destinations:
                filtered_destinations = destinations
                if search_term:
                    filtered_destinations = [d for d in filtered_destinations if search_term.lower() in d['name'].lower() or search_term.lower() in d['country'].lower()]
                if country_filter != "All":
                    filtered_destinations = [d for d in filtered_destinations if d['country'] == country_filter]
                
                for dest in filtered_destinations:
                    with st.expander(f"{dest['name']}, {dest['country']}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(f"**Description:** {dest['description']}")
                            st.write(f"**Climate:** {dest['climate']}")
                            st.write(f"**Best time to visit:** {dest['best_time_to_visit']}")
                        with col2:
                            if st.button(f"View Details", key=f"dest_{dest['destination_id']}"):
                                st.session_state.selected_destination = dest['destination_id']
                                st.rerun()
        
        with tab3:
            st.markdown('<h2 class="section-header">My Itineraries</h2>', unsafe_allow_html=True)
            
            # Create new itinerary
            with st.expander("Create New Itinerary", expanded=False):
                with st.form("create_itinerary"):
                    col1, col2 = st.columns(2)
                    with col1:
                        itinerary_name = st.text_input("Itinerary Name")
                        start_date = st.date_input("Start Date", value=datetime.now().date())
                    with col2:
                        end_date = st.date_input("End Date", value=datetime.now().date() + timedelta(days=7))
                    
                    # Simple itinerary details
                    st.write("**Itinerary Details:**")
                    days = (end_date - start_date).days + 1
                    itinerary_details = {"days": []}
                    
                    for day in range(1, days + 1):
                        day_activities = st.text_area(f"Day {day} Activities", placeholder="Enter activities separated by commas")
                        if day_activities:
                            itinerary_details["days"].append({
                                "day": day,
                                "activities": [act.strip() for act in day_activities.split(",")]
                            })
                    
                    if st.form_submit_button("Create Itinerary"):
                        if itinerary_name and start_date and end_date:
                            data = {
                                "name": itinerary_name,
                                "start_date": start_date.strftime("%Y-%m-%d"),
                                "end_date": end_date.strftime("%Y-%m-%d"),
                                "details_json": itinerary_details
                            }
                            response = make_api_request("/itineraries", method="POST", data=data, token=st.session_state.token)
                            if response:
                                st.success("Itinerary created successfully!")
                                st.rerun()
                        else:
                            st.error("Please fill in all required fields")
            
            # Display existing itineraries
            if itineraries:
                for itinerary in itineraries:
                    with st.expander(f"{itinerary['name']} ({itinerary['start_date']} to {itinerary['end_date']})"):
                        st.write(f"**Created:** {itinerary['created_at']}")
                        st.write("**Itinerary Details:**")
                        for day in itinerary['details_json'].get('days', []):
                            st.write(f"**Day {day['day']}:** {', '.join(day['activities'])}")
                        
                        # Export option
                        if st.button(f"Export to CSV", key=f"export_{itinerary['itinerary_id']}"):
                            # Create CSV data
                            csv_data = []
                            for day in itinerary['details_json'].get('days', []):
                                csv_data.append({
                                    'Day': day['day'],
                                    'Activities': ', '.join(day['activities'])
                                })
                            
                            df = pd.DataFrame(csv_data)
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name=f"{itinerary['name']}_itinerary.csv",
                                mime="text/csv"
                            )
            else:
                st.info("No itineraries found. Create your first itinerary above!")
        
        with tab4:
            st.markdown('<h2 class="section-header">AI Recommendations</h2>', unsafe_allow_html=True)
            
            # Recommendation form
            with st.form("recommendation_form"):
                st.markdown("### Get Personalized Recommendations")
                
                col1, col2 = st.columns(2)
                with col1:
                    destination_id = st.selectbox("Destination", [None] + [f"{d['name']}, {d['country']}" for d in destinations] if destinations else [None])
                    budget = st.number_input("Budget (USD)", min_value=0, value=1000, step=100)
                    duration = st.number_input("Duration (days)", min_value=1, value=7, step=1)
                
                with col2:
                    interests = st.multiselect("Interests", ["Culture", "Food", "Adventure", "Relaxation", "History", "Nature", "Nightlife", "Shopping"])
                    travel_style = st.selectbox("Travel Style", ["Budget", "Mid-range", "Luxury", "Backpacking", "Family", "Solo", "Couple"])
                
                if st.form_submit_button("Get Recommendations"):
                    if destination_id:
                        # Extract destination ID
                        dest_id = None
                        for d in destinations:
                            if f"{d['name']}, {d['country']}" == destination_id:
                                dest_id = d['destination_id']
                                break
                        
                        data = {
                            "destination_id": dest_id,
                            "budget": budget,
                            "duration": duration,
                            "interests": interests,
                            "travel_style": travel_style
                        }
                        
                        with st.spinner("Generating recommendations..."):
                            response = make_api_request("/recommendations", method="POST", data=data)
                            if response:
                                st.markdown("### 🤖 AI Recommendations")
                                st.markdown(response['recommendations'])
            
            # Generate complete itinerary
            st.markdown("---")
            with st.form("itinerary_generation_form"):
                st.markdown("### Generate Complete Itinerary")
                
                col1, col2 = st.columns(2)
                with col1:
                    gen_destination = st.selectbox("Destination", [f"{d['name']}, {d['country']}" for d in destinations] if destinations else [])
                    gen_budget = st.number_input("Budget (USD)", min_value=0, value=1500, step=100, key="gen_budget")
                    gen_duration = st.number_input("Duration (days)", min_value=1, value=5, step=1, key="gen_duration")
                
                with col2:
                    gen_interests = st.multiselect("Interests", ["Culture", "Food", "Adventure", "Relaxation", "History", "Nature", "Nightlife", "Shopping"], key="gen_interests")
                    gen_style = st.selectbox("Travel Style", ["Budget", "Mid-range", "Luxury", "Backpacking", "Family", "Solo", "Couple"], key="gen_style")
                
                if st.form_submit_button("Generate Itinerary"):
                    if gen_destination:
                        # Extract destination ID
                        dest_id = None
                        for d in destinations:
                            if f"{d['name']}, {d['country']}" == gen_destination:
                                dest_id = d['destination_id']
                                break
                        
                        data = {
                            "destination_id": dest_id,
                            "budget": gen_budget,
                            "duration": gen_duration,
                            "interests": gen_interests,
                            "travel_style": gen_style
                        }
                        
                        with st.spinner("Generating itinerary..."):
                            response = make_api_request("/itinerary/generate", method="POST", data=data)
                            if response:
                                st.markdown("### 📅 Generated Itinerary")
                                st.markdown(response['itinerary'])
        
        with tab5:
            st.markdown('<h2 class="section-header">Reviews</h2>', unsafe_allow_html=True)
            
            # Write a review
            with st.expander("Write a Review", expanded=False):
                with st.form("review_form"):
                    review_destination = st.selectbox("Select Destination", [f"{d['name']}, {d['country']}" for d in destinations] if destinations else [])
                    rating = st.slider("Rating", 1, 5, 5)
                    comment = st.text_area("Your Review", placeholder="Share your experience...")
                    
                    if st.form_submit_button("Submit Review"):
                        if review_destination and comment:
                            # Extract destination ID
                            dest_id = None
                            for d in destinations:
                                if f"{d['name']}, {d['country']}" == review_destination:
                                    dest_id = d['destination_id']
                                    break
                            
                            data = {
                                "destination_id": dest_id,
                                "rating": rating,
                                "comment": comment
                            }
                            
                            response = make_api_request("/reviews", method="POST", data=data, token=st.session_state.token)
                            if response:
                                st.success("Review submitted successfully!")
                                st.rerun()
                        else:
                            st.error("Please fill in all fields")
            
            # Display reviews
            reviews = make_api_request("/reviews")
            if reviews:
                for review in reviews:
                    # Get destination name
                    dest_name = "Unknown"
                    for d in destinations:
                        if d['destination_id'] == review['destination_id']:
                            dest_name = d['name']
                            break
                    
                    st.markdown(f"""
                    <div class="card">
                        <h4>{dest_name} - {review['rating']} ⭐</h4>
                        <p>{review['comment']}</p>
                        <small>Posted on: {review['created_at']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No reviews found.")

if __name__ == "__main__":
    main()
