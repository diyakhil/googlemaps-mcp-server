# tools/places_tool.py
def get_nearby_places(latitude: float, longitude: float, type:str = None) -> str:
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

    # Only include this field if type is passed
    if type:
        body["includedTypes"] = [type]

    try:
        response = requests.post(url, headers=headers, json=body)
        if not response.ok:
            return f"[HTTP Error {response.status_code}] {response.text[:150]}"
        data = response.json()
        places = data.get("places", [])
        if not places:
            return "No places found nearby."

        summaries = []
        for p in places:
            name = p.get("displayName", {}).get("text", "Unnamed place")
            address = p.get("formattedAddress", "no address available")
            rating = p.get("rating")
            if rating:
                summaries.append(f"{name}, rated {rating} stars, at {address}")
            else:
                summaries.append(f"{name} at {address}")

        if len(summaries) == 1:
            return f"I found one nearby place: {summaries[0]}."
        else:
            return "Here are some nearby places: " + "; ".join(summaries)

    except Exception as e:
        return f"Unhandled exception: {e}"
