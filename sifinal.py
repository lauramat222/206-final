import sqlite3
import requests
from typing import Optional, Dict, Any #

apikey = "t0OyBfrw3dS1yZjgLYIGCWrh68Pkb7bN"
baseurl = "https://app.ticketmaster.com/discovery/v2/events/"

def fetch_event_data(event_id: str, locale: str = "*", domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetches event data from Ticketmaster API with configurable parameters
    
    Args:
        event_id: The ID of the event (required)
        locale: ISO locale code (default '*')
        domain: Filter by domain availability (optional)
    
    Returns:
        Dictionary containing event data or None if request fails
    """
    params = {
        'apikey': apikey,
        'locale': locale
    }
    
    if domain:
        params['domain'] = domain
    
    try:
        response = requests.get(f"{BASE_URL}{event_id}.json", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    



    
