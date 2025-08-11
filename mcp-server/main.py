
from mcp.server.fastmcp import FastMCP
from typing import List
from tools.places_tool import get_nearby_places
from tools.maps_geocode_tool import maps_geocode, maps_reverse_geocode, maps_place

# In-memory mock database with 20 leave days to start
employee_leaves = {
    "E001": {"balance": 18, "history": ["2024-12-25", "2025-01-01"]},
    "E002": {"balance": 20, "history": []}
}

# Create MCP server
mcp = FastMCP("LeaveManager1")

# Tool: Check Leave Balance
@mcp.tool()
def get_leave_balance(employee_id: str) -> str:
    """Check how many leave days are left for the employee"""
    data = employee_leaves.get(employee_id)
    if data:
        return f"{employee_id} has {data['balance']} leave days remaining."
    return "Employee ID not found."

# Tool: Apply for Leave with specific dates
@mcp.tool()
def apply_leave(employee_id: str, leave_dates: List[str]) -> str:
    """
    Apply leave for specific dates (e.g., ["2025-04-17", "2025-05-01"])
    """
    if employee_id not in employee_leaves:
        return "Employee ID not found."

    requested_days = len(leave_dates)
    available_balance = employee_leaves[employee_id]["balance"]

    if available_balance < requested_days:
        return f"Insufficient leave balance. You requested {requested_days} day(s) but have only {available_balance}."

    # Deduct balance and add to history
    employee_leaves[employee_id]["balance"] -= requested_days
    employee_leaves[employee_id]["history"].extend(leave_dates)

    return f"Leave applied for {requested_days} day(s). Remaining balance: {employee_leaves[employee_id]['balance']}."


# Resource: Leave history
@mcp.tool()
def get_leave_history(employee_id: str) -> str:
    """Get leave history for the employee"""
    data = employee_leaves.get(employee_id)
    if data:
        history = ', '.join(data['history']) if data['history'] else "No leaves taken."
        return f"Leave history for {employee_id}: {history}"
    return "Employee ID not found."

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


# Resource: Greeting
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! How can I assist you with leave management today?"

if __name__ == "__main__":
    mcp.run()
