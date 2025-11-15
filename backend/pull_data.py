import requests
import json
import os
import time


def find_events(team_key, year):
    file_path = f"data/{team_key}/{year}.json"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open("api_key.txt", "r") as file:
        api_key = file.read().strip()

    headers = {'X-TBA-Auth-Key': api_key}

    url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/events/{year}/simple"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()

        with open(file_path, "w") as f:
            json.dump(json_data, f, indent=4)

    else:
        print(f"Error {response.status_code}: {response.text}")

def event(team_key, event_key):
    eventtime = 0
    file_path = f"data/{team_key}/{event_key}.json"

    # Make sure folder exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Check if file exists before reading
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                # Example: print the first actual_time value
                if data and "actual_time" in data[0 ]:
                    eventtime = data[0]["actual_time"]
                else:
                    print("it really fo me real")
            except json.JSONDecodeError:
                print("it be real")
    current_time = int(time.time())
    if current_time <= eventtime or eventtime == 0:
        with open("api_key.txt", "r") as file:
            api_key = file.read().strip()

        headers = {'X-TBA-Auth-Key': api_key}

        url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/event/{event_key}/matches"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            json_data = response.json()

            with open(file_path, "w") as f:
                json.dump(json_data, f, indent=4)

        else:
            print(f"Error {response.status_code}: {response.text}")
        return 0
    else:
        return 1


def read_events(file_path):
    with open(file_path, 'r') as f:
        events = json.load(f)
    return events


def pull_team_matches(team_key, year="2025"):
    url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/matches/{year}"
    return tba_request(url)

def pull_team_statuses(team_key, year="2025"):
    url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/events/{year}/statuses"
    return tba_request(url)

def pull_all_event_info(year="2025"):
    url = f"https://www.thebluealliance.com/api/v3/events/{year}/simple"
    response = tba_request(url)
    final = {}
    if response:
        for doc in response:
            final[doc["key"]] = doc
        with open("jsons/all_events.json", "w") as f:
            json.dump(final, f, indent=4)

def tba_request(url):
    import requests
    tba_key = os.getenv("TBA_KEY")
    year = "2025"
    headers = {'X-TBA-Auth-Key': tba_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result

    else:
        print(f"Error {response.status_code}: {response.text}")
        return False