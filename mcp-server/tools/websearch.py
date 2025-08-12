def web_search(query: str) -> str:
    import os
    import requests
    from dotenv import load_dotenv

    load_dotenv()
    API_KEY = os.getenv("CUSTOM_SEARCH_API_KEY")
    SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

    if not API_KEY:
        return "API key is missing. Check .env or environment variables."
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        results = data["items"][:5]
        
        formatted_results = []
        for i, item in enumerate(results, start=1):
            title = item.get("title", "No title")
            link = item.get("link", "No link")
            snippet = item.get("snippet", "No summary available")
            
            formatted_results.append(
                f"{i}. {title}\nSummary: {snippet}\n"
        )
        return "\n".join(formatted_results)
    
    except Exception as e:
        return f"Unhandled exception: {e}"