import requests
import json
from env_vars import TBA_KEY

def tba_request(api_url: str):
    """Sends a single web request to the TBA API v3.

    # Parameters
    - `api_url`: suffix of the API request URL (the part after '/api/v3/').
    - `modify`: if True, we calculate certain more useful datapoints before returning it

    # Returns
    The data recieved by the TBA API
    """
    full_url = f"https://www.thebluealliance.com/api/v3/{api_url}"
    request_headers = {"X-TBA-Auth-Key": TBA_KEY}

    try:
        request = requests.get(full_url, headers=request_headers)
    except requests.exceptions.ConnectionError:
        print("No internet connection.")
        return None

    if request.status_code != 200:
        print(f"TBA API returned status {request.status_code} for {api_url}")
        return None

    response = request.json()

    return response