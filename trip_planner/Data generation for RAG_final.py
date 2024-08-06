#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import random
import pandas as pd
import time


# In[2]:


api_key='API-KEY'


# In[3]:


# Comprehensive categories and cities/towns
categories = [
    'historical sites', 'museums', 'parks', 'landmarks', 'entertainment venues',
    'shopping centers', 'beaches', 'theatres', 'galleries', 'zoos', 'aquariums',
    'amusement parks', 'gardens', 'castles', 'hiking trails', 'nature reserves',
    'libraries', 'sports venues', 'concert halls', 'markets'
]

# categories = [
#     'historical sites']


# city = [
#     'London', 'Manchester', 'Edinburgh', 'Birmingham', 'Glasgow', 'Liverpool',
#     'Bristol', 'Leeds', 'Cardiff', 'Belfast', 'Newcastle', 'Sheffield', 'Nottingham',
#     'Leicester', 'York', 'Cambridge', 'Oxford', 'Bath', 'Aberdeen', 'Inverness',
#     'Dundee', 'Plymouth', 'Norwich', 'Southampton', 'Brighton'
# ]

city = 'London'



# In[4]:


# Additional queries for accommodation and dining
accommodation_query = f"hotels in {city}"
dining_query = f"restaurants in {city}"

# Generate list of queries
queries = [f"{category} in {city}" for category in categories] + [accommodation_query, dining_query]


# In[5]:


queries


# In[6]:


# Function to fetch data from Google Places API with retry mechanism
def fetch_places_data(query, retries=3, backoff_factor=0.3):
    endpoint = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    parameters = {
        'query': query,
        'key': api_key
    }
    for attempt in range(retries):
        try:
            response = requests.get(endpoint, params=parameters)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"All {retries} attempts failed.")
                return None


# In[7]:


# Function to fetch place details using Place Details API with retry mechanism
def fetch_place_details(place_id, retries=3, backoff_factor=0.3):
    endpoint = 'https://maps.googleapis.com/maps/api/place/details/json'
    parameters = {
        'place_id': place_id,
        'key': api_key
    }
    for attempt in range(retries):
        try:
            response = requests.get(endpoint, params=parameters)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"All {retries} attempts failed.")
                return None


# In[8]:


# Function to fetch transportation details using Directions API
def fetch_transport_details(origin, destination, mode, retries=3, backoff_factor=0.3):
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json'
    parameters = {
        'origin': origin,
        'destination': destination,
        'mode': mode,
        'key': api_key
    }
    for attempt in range(retries):
        try:
            response = requests.get(endpoint, params=parameters)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"All {retries} attempts failed.")
                return None


# In[9]:


# Function to process the API response and extract relevant details
def process_places_data(data, type_of_place):
    places = []
    if data and 'results' in data:
        for place in data['results']:
            place_id = place['place_id']
            details = fetch_place_details(place_id)
            description = details['result'].get('editorial_summary', {}).get('overview', 'No description available')
            price_level = details['result'].get('price_level', 'N/A')
            user_ratings_total = place.get('user_ratings_total', 'N/A')
            rating = place.get('rating', 'N/A')
            # Approximate cost estimation
            if price_level == 0:
                cost = "$0 (Free)"
            elif price_level == 1:
                cost = "$1 - $20 (Inexpensive)"
            elif price_level == 2:
                cost = "$20 - $50 (Moderate)"
            elif price_level == 3:
                cost = "$50 - $100 (Expensive)"
            elif price_level == 4:
                cost = "$100+ (Very Expensive)"
            else:
                cost = "Unknown"
            
            # Comprehensive suitability categories mapping
            suitability_categories = {
                'family': ['park', 'zoo', 'museum', 'nature reserve', 'amusement park', 'restaurant', 'beach', 'aquarium', 'historical site', 'shopping mall', 'garden'],
                'couples': ['restaurant', 'landmark', 'theatre', 'concert hall', 'garden', 'wine bar', 'romantic place', 'museum', 'spa', 'fine dining'],
                'friends': ['shopping mall', 'market', 'sports venue', 'concert hall', 'bar', 'club', 'restaurant', 'hiking trail', 'amusement park', 'historical site'],
                'colleagues': ['conference center', 'business park', 'sports venue', 'fine dining', 'restaurant', 'bar', 'landmark', 'theatre', 'golf course']
            }

            # Check if the place's types match any of the suitability categories
            suitability = {
                'family': any(cat in place.get('types', []) for cat in suitability_categories['family']),
                'couples': any(cat in place.get('types', []) for cat in suitability_categories['couples']),
                'friends': any(cat in place.get('types', []) for cat in suitability_categories['friends']),
                'colleagues': any(cat in place.get('types', []) for cat in suitability_categories['colleagues']),
            }
            
            
            place_info = {
                'name': place['name'],
                'address': place.get('formatted_address', 'N/A'),
                'rating': rating,
                'user_ratings_total': user_ratings_total,
                'types': place.get('types', 'N/A'),
                'latitude': place['geometry']['location']['lat'],
                'longitude': place['geometry']['location']['lng'],
                'description': description,
                'cost': cost,
                'suitability': suitability,
                'place_id': place_id  # Storing place_id for transport calculation
            }
            places.append(place_info)
            time.sleep(1)  # To avoid hitting the rate limit for Place Details API
    return places


# In[10]:


# Function to fetch and process data for a list of queries
def get_places_data(queries):
    all_places = []
    for query in queries:
        print(f"Fetching data for query: {query}")
        type_of_place = query.split(' in ')[0]
        data = fetch_places_data(query)
        places = process_places_data(data, type_of_place)
        all_places.extend(places)
        time.sleep(1)  # To avoid hitting the rate limit for Text Search API
    return all_places


# In[11]:


# Function to fetch transport details between places with different modes
def get_transport_details(places):
    transport_data = []
    modes = ['driving', 'walking', 'bicycling', 'transit']  # Modes of transport
    for i in range(len(places) - 1):
        origin = f"{places[i]['latitude']},{places[i]['longitude']}"
        destination = f"{places[i + 1]['latitude']},{places[i + 1]['longitude']}"
        for mode in modes:
            transport_info = fetch_transport_details(origin, destination, mode)
            if transport_info and 'routes' in transport_info and len(transport_info['routes']) > 0:
                route = transport_info['routes'][0]['legs'][0]
                transport_detail = {
                    'from': places[i]['name'],
                    'to': places[i + 1]['name'],
                    'distance': route['distance']['text'],
                    'duration': route['duration']['text'],
                    'mode': mode.capitalize()
                }
                transport_data.append(transport_detail)
    return transport_data


# In[12]:


# Estimate time and cost
text_search_requests = len(queries)

# Dynamically calculate the average number of place details requests
place_details_requests = sum(len(fetch_places_data(query).get('results', [])) for query in queries)

time_per_text_search = 1  # seconds (adjust based on observation)
time_per_detail_search = 1  # seconds (adjust based on observation)

total_time = text_search_requests * time_per_text_search + place_details_requests * time_per_detail_search
total_time_minutes = total_time / 60

# Ensure these costs are accurate as per current Google Cloud pricing
text_search_cost_per_1000 = 7  # USD (check the latest pricing)
place_details_cost_per_1000 = 17  # USD (check the latest pricing)

total_cost = (text_search_requests / 1000 * text_search_cost_per_1000) + (place_details_requests / 1000 * place_details_cost_per_1000)

print(f"Estimated total time: {total_time_minutes:.2f} minutes")
print(f"Estimated total cost: ${total_cost:.2f}")


# In[13]:


# Fetch and process the data
places_data = get_places_data(queries)

# Fetch transportation details between places
transport_data = get_transport_details(places_data)



# In[14]:


df_places = pd.DataFrame(places_data)
df_transport=pd.DataFrame(transport_data)


# In[15]:


# df_transport.columns


# In[16]:


df_places_std=pd.DataFrame()
df_transport_std=pd.DataFrame()


# In[17]:


df_places_std[['name', 'address', 'rating', 'user_ratings_total', 'types', 'latitude',
       'longitude', 'description', 'cost', 'suitability', 'place_id']]=df_places[['name', 'address', 'rating', 'user_ratings_total', 'types', 'latitude',
       'longitude', 'description', 'cost', 'suitability', 'place_id']].astype(str)

df_transport_std[['from', 'to', 'distance', 'duration', 'mode']]=df_transport[['from', 'to', 'distance', 'duration', 'mode']].astype(str)
                                                                           


# In[18]:


import os
from google.cloud import bigquery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='API.json'
client=bigquery.Client(project='genai-projects-431020')


# In[19]:


table_id='genai-projects-431020.google_data.places_data_london_by_category_3007'
job_config=bigquery.LoadJobConfig(autodetect=True, write_disposition='WRITE_TRUNCATE')

job=client.load_table_from_dataframe(df_places_std, table_id, job_config=job_config)
job.result()

print(f"Loaded {job.output_rows} rows into {table_id}.")


# In[20]:


table_id='genai-projects-431020.google_data.transport_data_london_by_category_3007'
job_config=bigquery.LoadJobConfig(autodetect=True, write_disposition='WRITE_TRUNCATE')
job=client.load_table_from_dataframe(df_transport_std, table_id, job_config=job_config)
job.result()

print(f"Loaded {job.output_rows} rows into {table_id}.")

