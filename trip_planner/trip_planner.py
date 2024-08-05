import streamlit as st
import pickle
import faiss
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings

# Load the FAISS index
index = faiss.read_index('faiss_index.bin')

# Load the chunks, docstore, and index-to-docstore-id mapping
with open('chunks.pkl', 'rb') as f:
    chunks = pickle.load(f)

with open('docstore.pkl', 'rb') as f:
    docstore = pickle.load(f)

with open('index_to_docstore_id.pkl', 'rb') as f:
    index_to_docstore_id = pickle.load(f)

# Initialize OpenAI embeddings (same model used before)
embeddings_openai = OpenAIEmbeddings(model='text-embedding-ada-002')

# Recreate the FAISS vector store and retriever
faiss_vector_store = FAISS(embedding_function=embeddings_openai,
                           index=index,
                           docstore=docstore,
                           index_to_docstore_id=index_to_docstore_id)
best_retriever = faiss_vector_store.as_retriever(search_kwargs={'k': 7})

# Set the best temperature value
best_temperature = 0.3

# Initialize the LLM with the best temperature (API key is already set in the environment)
llm = OpenAI(temperature=best_temperature, max_tokens=1000)

# Set up the page configuration for aesthetics
st.set_page_config(page_title="Itinerary Planner", page_icon="🗺️", layout="centered")

# Main title for the app
st.title("🗺️ London Itinerary Planner")

# Define categories, cost levels, and people types
categories = [
    'historical sites', 'museums', 'parks', 'landmarks', 'entertainment venues',
    'shopping centers', 'beaches', 'theatres', 'galleries', 'zoos', 'aquariums',
    'amusement parks', 'gardens', 'castles', 'hiking trails', 'nature reserves',
    'libraries', 'sports venues', 'concert halls', 'markets', 'hotels', 'restaurants'
]
cost_levels = ["$0 (Free)", "$1 - $20 (Inexpensive)", "$20 - $50 (Moderate)", "$50 - $100 (Expensive)", "$100+ (Very Expensive)", "Unknown"]
people_types = ["family", "friends", "couples", "colleagues"]

# User inputs
st.sidebar.header("Trip Preferences")
destination = st.sidebar.text_input("Destination", "London")
travel_days = st.sidebar.number_input("Number of Travel Days", min_value=1, max_value=30, value=3)
interests = st.sidebar.multiselect("Interests", categories)
transport_mode = st.sidebar.selectbox("Preferred Transport Mode", ["Walking", "Public Transport", "Driving"])
budget = st.sidebar.radio("Budget", ["Low", "Medium", "High"])
people_type = st.sidebar.radio("People Type", people_types)

# Function to generate the itinerary
@st.cache_data
def generate_itinerary(destination, travel_days, interests, transport_mode, budget, people_type):
    full_itinerary = []
    
    for i in range(1, travel_days + 1):
        sample_itinerary = (
            f"Day {i}:\n"
            "- Morning: Breakfast at The Breakfast Club, Soho (English, £25 for two). Stroll through Hyde Park, visit the Serpentine Gallery. Free entry.\n"
            "- Afternoon: Lunch at Pret A Manger, South Kensington (Light bites, £15 for two). Shop at Oxford Street (Primark, Zara, £100 budget). Explore Regent's Park. Free entry.\n"
            "- Evening: Dinner at Flat Iron, Covent Garden (Steak, £40 for two). Walk along the Thames River from Southbank to London Eye. Free.\n"
            "- Night: Stay at Premier Inn or similar, Central London. £100 per night.\n\n"

            f"Day {i+1}:\n"
            "- Morning: Breakfast at Hotel or Greggs (Quick bites, £10 for two). Train to Brighton from London Victoria (£30 round trip for two). Relax at Brighton Beach, explore Brighton Pier. Free.\n"
            "- Afternoon: Lunch at The Regency Restaurant, Brighton (Fish and chips, £25 for two). Explore The Lanes for shopping (£50 budget). Visit Brighton Pavilion (£30 for two).\n"
            "- Evening: Dinner at Wahaca, Soho (Mexican street food, £35 for two). Evening stroll at Trafalgar Square. Free.\n"
            "- Night: Return to Premier Inn or similar, Central London. £100 per night.\n\n"

            "Total Cost: Approximately £625, including food, accommodation, travel, shopping, and attractions.\n"
        )
        
        query = (
            f"Plan day {i} of a {travel_days}-day trip to {destination} for {people_type}. "
            f"Include recommendations for breakfast, morning activities, lunch, afternoon activities, dinner, and evening activities. "
            f"Ensure the plan is suitable for {budget} travelers."
        )
        
        # Run the query using the RetrievalQA chain
        chain = RetrievalQA.from_chain_type(llm=llm, retriever=best_retriever, chain_type="stuff")
        response = chain.run(sample_itinerary + query)
        
        # Extract and clean the day's details
        if "Day " in response:
            itinerary_split = response.split("Day ")
            if len(itinerary_split) > i:
                day_details = itinerary_split[i].strip().lstrip("1234567890: ")
            else:
                day_details = "No details returned."
        else:
            day_details = "No details returned."
        
        full_itinerary.append({"day": i, "activity": f"Activities for day {i}", "details": day_details})
    
    return full_itinerary

# Function to format the itinerary to ensure proper cost formatting and natural language flow
def format_itinerary(itinerary, currency_symbol="£"):
    formatted_itinerary = []
    for day in itinerary:
        details = day["details"]

        # Adjust formatting for cost per person with the correct currency symbol
        details = details.replace("20—50", f"{currency_symbol}20-{currency_symbol}50 per person")
        details = details.replace("50—100", f"{currency_symbol}50-{currency_symbol}100 per person")
        details = details.replace("15—25", f"{currency_symbol}15-{currency_symbol}25 per person")
        details = details.replace("30—40", f"{currency_symbol}30-{currency_symbol}40 per person")
        
        # Add any other necessary formatting adjustments here
        formatted_itinerary.append(f"Day {day['day']}: {details}")
    
    return "\n".join(formatted_itinerary)

# Updated section in Streamlit to generate and display the itinerary
if st.sidebar.button("Generate Itinerary"):
    # Generate the itinerary
    itinerary = generate_itinerary(destination, travel_days, interests, transport_mode, budget, people_type)
    
    # Format the itinerary for better readability and natural language flow
    formatted_itinerary = format_itinerary(itinerary, currency_symbol="£")  # Replace "£" with "$" or another currency symbol as needed
    
    # Display the formatted itinerary in the Streamlit app
    st.subheader(f"Your {travel_days}-Day Itinerary for {destination}")
    
    # Split the formatted itinerary by day and display it
    for day_plan in formatted_itinerary.split("Day ")[1:]:
        # Safely split the day number and details
        if ":" in day_plan:
            day_number, details = day_plan.split(":", 1)
            st.markdown(f"### Day {day_number.strip()}")
            st.write(details.strip())
        else:
            st.write(day_plan.strip())  # Handle cases where the day plan doesn't follow the expected format

# Styling for better aesthetics with higher specificity
st.markdown(
    """
    <style>
    /* Apply white background to the main app container */
    .reportview-container .main .block-container {
        background-color: #FFFFFF;  /* Main content background white */
        padding: 20px;
        border-radius: 10px;
    }
    
    /* Set the background color for the sidebar */
    .sidebar .sidebar-content {
        background-color: #000000;  /* Black background for the sidebar */
    }
    
    /* Set the overall page background to white */
    .reportview-container {
        background-color: #FFFFFF;  /* Entire page background white */
    }
    
    /* Customize the title */
    h1 {
        color: #FFFFFF;  /* White title color */
        text-align: center;
    }
    
    /* Customize the subheaders and other headers */
    h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;  /* White headers */
    }
    
    /* Customize the buttons */
    .stButton button {
        background-color: #000000;  /* Black button background */
        color: #FFFFFF;  /* White text color for the button */
        border-radius: 5px;
    }

    /* Change the color of selected user inputs */
    .stMultiSelect > div > div > div {
        color: #FFFFFF !important;
        background-color: #000000 !important;  /* Black background for inputs */
    }

    .stRadio > div > div > label > div {
        color: #FFFFFF !important;
    }

    .stSelectbox > div > div > div {
        color: #FFFFFF !important;
        background-color: #000000 !important;  /* Black background for inputs */
    }
    </style>
    """, unsafe_allow_html=True
)
