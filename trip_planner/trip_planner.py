import streamlit as st
import openai
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Set a limit for API calls per session and time window
CALL_LIMIT = 5
TIME_WINDOW = 3600  # 1 hour in seconds

if 'api_call_count' not in st.session_state:
    st.session_state.api_call_count = 0
    st.session_state.start_time = time.time()

def user_input_form():
    st.title("Trip Planner - Demo")
    destination = st.text_input("Destination", "Paris")
    travel_dates = st.text_input("Travel Dates", "June 10 - June 20")
    interests = st.text_input("Interests", "Museums, Food, History")
    if st.button("Plan My Trip"):
        return destination, travel_dates, interests
    return None, None, None

def generate_trip_suggestions(destination, travel_dates, interests):
    prompt = f"I am planning a trip to {destination} from {travel_dates}. I am interested in {interests}. Can you suggest an itinerary?"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message["content"].strip()

def main():
    current_time = time.time()
    elapsed_time = current_time - st.session_state.start_time

    if elapsed_time > TIME_WINDOW:
        st.session_state.api_call_count = 0
        st.session_state.start_time = current_time

    if st.session_state.api_call_count >= CALL_LIMIT:
        st.warning("API call limit reached. Please try again later.")
        return

    destination, travel_dates, interests = user_input_form()
    if destination and travel_dates and interests:
        with st.spinner("Generating trip suggestions..."):
            suggestions = generate_trip_suggestions(destination, travel_dates, interests)
            st.session_state.api_call_count += 1
            st.subheader("Your Trip Itinerary:")
            st.write(suggestions)
            st.info(f"API calls used: {st.session_state.api_call_count}/{CALL_LIMIT}")

if __name__ == "__main__":
    main()
