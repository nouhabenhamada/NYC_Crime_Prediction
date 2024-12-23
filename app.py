import streamlit as st
import pandas as pd
import joblib
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster, ClickForLatLng
from geopy.exc import GeocoderTimedOut

# Load the trained model using joblib
model = joblib.load('xgb_model.joblib')  # Update with the actual path to your saved model file

# Define the LOCATION_CODE mapping you used during training
location_code_map = {'87G8R3PJ+': 0}  # Example, make sure to extend with other location codes

# Function to get location code from latitude and longitude using a geolocator (Nominatim)
def get_location_code(lat, lon):
    try:
        geolocator = Nominatim(user_agent="streamlit_app")
        location = geolocator.reverse((lat, lon), exactly_one=True, timeout=10)

        # Get the address or location description
        address = location.raw.get('address', {})

        # Check if the location information has a valid location code mapping
        for key, code in location_code_map.items():
            # Example method, improve mapping using address for matching location code
            if key in address.get('postcode', ''):
                return key, code
        return None, -1  # Return None if no location code is found
    except GeocoderTimedOut:
        return None, -1

# Streamlit app interface
st.title("New York City Crime Prediction")
st.write("""
    This app predicts crime based on several factors, including location clicked on the map.
    Tap on the map to select a location, and then the model will predict the crime likelihood.
""")

# Create the map centered on New York City
map_center = [40.7128, -74.0060]  # Latitude and Longitude of New York City
m = folium.Map(location=map_center, zoom_start=12)

# Add MarkerCluster
marker_cluster = MarkerCluster().add_to(m)

# Function to handle click and add marker to map
def handle_map_click(lat, lon):
    location_code, code = get_location_code(lat, lon)
    if location_code:
        st.write(f"You clicked at latitude: {lat}, longitude: {lon}")
        st.write(f"Mapped Location Code: {location_code}, Numeric Code: {code}")

        # Predict crime with other required user inputs
        crime_prediction = predict_crime(year=2023, month=12, hour_input=15, weekday=5,
                                         address_precinct=10, crime_class=0,
                                         age_group=3, race=1, sex=0, location_code=code)
        st.write(f"Predicted Crime Likelihood: {crime_prediction:.2f}")
    else:
        st.write("Could not map location to crime prediction.")

# Create a function to handle the click event
def click_callback(e):
    lat, lon = e.latlng
    handle_map_click(lat, lon)

# Add ClickForLatLng to the map
click_latlng = ClickForLatLng(callback=click_callback)
m.add_child(click_latlng)

# Display the map with Streamlit
st.write("Click on the map to choose a location:")
st.markdown(folium.Figure().add_child(m)._repr_html_(), unsafe_allow_html=True)

# This function makes the crime prediction based on inputs
def predict_crime(year, month, hour_input, weekday, address_precinct, crime_class,
                  age_group, race, sex, location_code):
    # Prepare user input data
    user_input = pd.DataFrame({
        'year': [year],
        'month': [month],
        'hour': [hour_input],
        'weekday': [weekday],
        'ADDR_PCT_CD': [address_precinct],
        'CRIME_CLASS': [crime_class],
        'VIC_AGE_GROUP': [age_group],
        'VIC_RACE': [race],
        'VIC_SEX': [sex],
        'LOCATION_CODE': [location_code],  # Encoded LOCATION_CODE
    })

    # Predict crime using the trained model
    prediction = model.predict(user_input)

    return prediction[0]  # Return prediction (assuming it returns a numeric value)
