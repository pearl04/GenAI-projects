import streamlit as st
import openai
from openai import OpenAI
import os

# Fetch API key from Streamlit secrets
#openai.api_key=st.secrets['open_ai']['api_key']
# Initialize the Streamlit app
st.title("OpenAI Chatbot")

# Fetch API key from Streamlit secrets
#openai.api_key = st.secrets["openai"]["api_key"]
# Set a limit for API calls per session
#CALL_LIMIT = 5

def user_input_form():
    st.title("Trip Planner - Demo")
    destination = st.text_input("Destination", "Paris")
    travel_dates = st.text_input("Travel Dates", "June 10 - June 20")
    interests = st.text_input("Interests", "Museums, Food, History")
    transport_mode=st.text_input("Public transport")
    budget=st.text_input("500$")
    people=st.text_input("2")
    if st.button("Plan My Trip"):
        return destination, travel_dates, interests, transport_mode, budget, people
    return None, None, None, None, None, None

def generate_trip_suggestions(destination, travel_dates, interests, transport_mode, budget,people):
    prompt = f"I am planning a trip to {destination} from {travel_dates}. I am interested in {interests}. My budget is {budget} and I would prefer travelling within place by {transport_mode}. We are {people} travelling . Can you suggest a detailed itinerary?"
    client = OpenAI(st.secrets['open_ai']['api_key'])
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a very enthusiastic trip planning assistant."},
            {"role": "user", "content": prompt}
        ],
        #max_tokens=150
    )
    return response.choices[0].message['content'].strip()

def main():
    destination, travel_dates, interests, transport_mode, budget, people = user_input_form()
    if destination and travel_dates and interests and transport_mode and budget and people:
        with st.spinner("Generating trip suggestions..."):
            suggestions = generate_trip_suggestions(destination, travel_dates, interests, transport_mode, budget, people)
            #st.session_state.api_call_count += 1
            st.subheader("Your Trip Itinerary:")
            st.write(suggestions)
           # st.info(f"API calls used: {st.session_state.api_call_count}/{CALL_LIMIT}")

if __name__ == "__main__":
    main()

