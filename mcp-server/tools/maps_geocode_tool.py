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

def maps_get_directions(origin: str, destination: str, mode='driving', alternatives=True) -> dict: 
    try: 
        result = gmaps.directions(origin=origin, destination=destination, mode=mode, alternatives=alternatives)
        steps = result[0]["legs"][0]["steps"]
        if not result: 
            return "No results found for the provided origin and destination"
        instructions = ". ".join([step["html_instructions"] for step in steps])
        return {"directions": instructions}
    except Exception as e: 
        return f"Unhandled exception in get directions tool: {e}"

def maps_travel_time(origin: str, destination: str, mode='driving') -> dict:
    try:
        result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode=mode)
        if not result.get("rows"):
            return "No results found for the provided origin and destination."
        element = result["rows"][0]["elements"][0]
        return {
            "distance": element["distance"]["text"],
            "duration": element["duration"]["text"]
        }
    except Exception as e:
        return f"Unhandled exception in travel_time tool: {e}"