from dotenv import load_dotenv
import googlemaps
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

def maps_geocode(address: str) -> dict:
    try: 
        result = gmaps.geocode(address)
        if not result:
            return "No results found for the provided address."
        #Gets the first element in the results array 
        return result[0]["geometry"]["location"]
    except Exception as e: 
        return f"Unhandled exception in geocode tool: {e}"

def maps_reverse_geocode(latitude: float, longitude: float,) -> dict: 
    try: 
        result = gmaps.reverse_geocode((latitude, longitude))
        if not result: 
            return "No results found for the provided lat long."
        return result[0]["formatted_address"]
    except Exception as e: 
        return f"Unhandled exception in reverse geocode tool: {e}"

