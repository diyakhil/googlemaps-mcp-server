# tools/places_tool.py
def get_nearby_places(latitude: float, longitude: float) -> str:
    """Return nearby places given latitude and longitude"""
    import os
    import requests
    from dotenv import load_dotenv

    load_dotenv()
    API_KEY = os.getenv("API_KEY")

    if not API_KEY:
        return "API key is missing. Check .env or environment variables."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress"
    }

    body = {
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": 1000
            }
        },
        "maxResultCount": 3
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        if not response.ok:
            return f"[HTTP Error {response.status_code}] {response.text[:150]}"
        data = response.json()
        places = data.get("places", [])
        if not places:
            return "No places found nearby."

        first = places[0]
        name = first.get("displayName", {}).get("text", "Unnamed place")
        address = first.get("formattedAddress", "No address")
        return f"One nearby place: {name} at {address}"

    except Exception as e:
        return f"Unhandled exception: {e}"
