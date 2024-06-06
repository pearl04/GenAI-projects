import streamlit as st
import openai
from openai import OpenAI
import os

# Initialize the Streamlit app
st.title("OpenAI Chatbot")

# Sidebar for API key input
with st.sidebar:
    st.header("Enter your OpenAI API Key")
    user_api_key = st.text_input("OpenAI API Key", type="password")
    st.write("[Get your OpenAI API key](https://platform.openai.com/account/api-keys)")

# Default API key for users without their own key
default_api_key = st.secrets["open_ai"]["api_key"]

if "default_key_usage" not in st.session_state:
    st.session_state.default_key_usage = 0

# Fetch API key from user input
if user_api_key:
    api_key = user_api_key
else:
    api_key = default_api_key
    if st.session_state.default_key_usage >= 1:
        st.warning("Default API key usage limit reached.")
        api_key = None

if api_key:
    openai.api_key = api_key
else:
    st.warning("Please enter your OpenAI API key.")

def user_input_form():
    st.title("Trip Planner - Demo")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        destination = st.text_input("Destination", "Paris")
        travel_dates = st.text_input("Travel Dates", "June 10 - June 20")
        interests = st.text_input("Interests", "Museums, Food, History")
        transport_mode = st.text_input("Transport mode preferred", "Public transport")
        
    with col2:
        budget = st.text_input("Approx. budget (mention currency)", "500$")
        people = st.text_input("Number of people travelling", "2")
        
    if st.button("Plan My Trip"):
        return destination, travel_dates, interests, transport_mode, budget, people
    return None, None, None, None, None, None


def generate_trip_suggestions(destination, travel_dates, interests, transport_mode, budget,people):
    prompt = f"I am planning a trip to {destination} from {travel_dates}. I am interested in {interests}. My budget is {budget} and I would prefer travelling within place by {transport_mode}. We are {people} travelling . Can you suggest a detailed itinerary?"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a very enthusiastic trip planning assistant."},
            {"role": "user", "content": prompt}
        ],
        #max_tokens=150
    )
    #return response.choices[0].message['content'].strip()
    return response.choices[0].message.content
def main():
    if api_key:
        destination, travel_dates, interests, transport_mode, budget, people = user_input_form()
        if destination and travel_dates and interests and transport_mode and budget and people:
            if not user_api_key:
                if st.session_state.default_key_usage < 1:
                    with st.spinner("Generating trip suggestions..."):
                        suggestions = generate_trip_suggestions(destination, travel_dates, interests, transport_mode, budget, people)
                        st.session_state.default_key_usage += 1
                        st.subheader("Your Trip Itinerary:")
                        st.write(suggestions)
                else:
                    st.warning("Default API key usage limit reached. Please enter your own API key.")
            else:
                with st.spinner("Generating trip suggestions..."):
                    suggestions = generate_trip_suggestions(destination, travel_dates, interests, transport_mode, budget, people)
                    st.subheader("Your Trip Itinerary:")
                    st.write(suggestions)
    # else:
    #     st.warning("Please enter your OpenAI API key.")

if __name__ == "__main__":
    main()
