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

def maps_reverse_geocode(latitude: float, longitude: float) -> dict: 
    try: 
        result = gmaps.reverse_geocode((latitude, longitude))
        if not result: 
            return "No results found for the provided lat long."
        return result[0]["formatted_address"]
    except Exception as e: 
        return f"Unhandled exception in reverse geocode tool: {e}"

def maps_place(place_id: str) -> dict : 
    #An example place id for Qahwah House: ChIJk4hAbgARsYkRVgYFTwm3Iw8
    try: 
        #FieldsMask is necessary for different resposne fields to be returned 
        result = gmaps.place(place_id = place_id, fields=[ 
            "name","website"])
        if not result: 
            return "No results found for the provided placeId"
        return result
    except Exception as e: 
        return f"Unhandled exception in place tool: {e}"