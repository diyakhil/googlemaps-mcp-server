def get_places_nearby_name(latitude: float, longitude: float, locationName: str, category: str) -> str:
    import os
    import requests
    from dotenv import load_dotenv

    print(f"Loading environment variables...")
    load_dotenv()
    API_KEY = os.getenv("GEOAPIFY_API_KEY")

    if not API_KEY:
        print("API key is missing. Check .env or environment variables.")
        return "API key is missing. Check .env or environment variables."

    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    url = f"https://api.geoapify.com/v2/places?apiKey={API_KEY}&categories={category}&filter=circle:{longitude},{latitude},10000&limit=10&name={locationName}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return f"[HTTP Error {response.status_code}] {response.text[:150]}"

    response_json = response.json()

    features = response_json.get("features", [])
    if not features:
        return "No places found nearby."

    summaries = []
    for f in features:
        props = f.get("properties", {})
        name = props.get("name") or "Unnamed place"
        distance = props.get("distance", None)
        address = props.get("address", "no address available")
        coordinates = f.get("geometry", {}).get("coordinates", [None, None])
        lon, lat = coordinates if len(coordinates) == 2 else (None, None)

        # Build description
        desc_parts = [f"{name}"]
        if distance is not None:
            desc_parts.append(f"({round(distance, 1)} m away)")
        desc_parts.append(f"at {address}")
        if lat and lon:
            desc_parts.append(f"[lat: {lat}, lon: {lon}]")

        summaries.append(" ".join(desc_parts))

    # Join results like the Google Places example
    if len(summaries) == 1:
        return f"I found one nearby place: {summaries[0]}."
    else:
        return "Here are some nearby places: " + "; ".join(summaries)