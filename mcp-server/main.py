
from fastmcp import FastMCP
from typing import List
from tools.places_tool import get_nearby_places
from tools.maps_geocode_tool import maps_geocode, maps_reverse_geocode, maps_place, maps_get_directions, maps_travel_time
from tools.websearch import web_search

# Create MCP server
mcp = FastMCP("LeaveManager1")

# Tool: Check first nearby location, valid included types are here https://developers.google.com/maps/documentation/places/web-service/legacy/supported_types
@mcp.tool()
def get_nearby_places_wrapper(latitude: float, longitude: float, type:str = None) -> str:
    """Return nearby places given latitude, longitude, and specific type of location"""
    return get_nearby_places(latitude, longitude, type)

@mcp.tool()
def maps_geocode_wrapper(address: str) -> dict:
    """ Return latitude longitude coordinates from a formatted address """
    return maps_geocode(address)

@mcp.tool()
def maps_reverse_geocode_wrapper(latitude: float, longitude: float) -> dict:
    """ Return formatted address from a set of lat long coordinates """
    return maps_reverse_geocode(latitude, longitude)

@mcp.tool()
def maps_place_wrapper(place_id: str) -> dict:
    """ Returns metadata about a place given a placeId """
    return maps_place(place_id)

@mcp.tool()
def maps_get_directions_wrapper(origin: str, destination: str) -> dict:
    """ Returns directions from origin to destination """
    return maps_get_directions(origin, destination)

@mcp.tool()
def maps_travel_time_wrapper(origin: str, destination: str) -> dict:
    """ Returns travel time and distance from origin to destination """
    return maps_travel_time(origin, destination)

# @mcp.tool()
# def get_place_photo(latitude: float, longitude: float) -> dict: 
#     """ Returns the place photo for a passed in given location """
#     # address = maps_reverse_geocode_wrapper(latitude, longitude)
#     place_id = maps_places(latitude, longitude, 1)
#     return place_id
#     # return maps_place(place_id)


@mcp.tool()
def handle_unknown(query: str) -> str:
    """
    Handle queries that don't match any known tool.
    Falls back to web search.
    """
    return web_search(query)

# Resource: Greeting
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! How can I assist you with leave management today?"

if __name__ == "__main__":
    mcp.run()
