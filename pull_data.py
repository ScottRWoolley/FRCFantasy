import requests
import json
# pip install statbotics==2.0.1
import statbotics
import os

def pull_year(year):
    page_num = 0
    page = True
    file_path = "data/teams.json"
    with open("api_key.txt", "r") as file:
        api_key = file.read()
    headers = { 'X-TBA-Auth-Key': api_key }
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Create the file if it does not exist yet
    if not os.path.isfile(file_path):
        with open(file_path, "w") as f:
            json.dump({}, f, indent=4)

    while page:
        print(page_num)
        url = f"https://www.thebluealliance.com/api/v3/teams/{year}/{page_num}/simple"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            json_data = response.json()
            if len(json_data) < 1:
                page = False
            with open(file_path, "r") as f:
                data = json.load(f)
            if 'teams' not in data:
                data['teams'] = []
            data['teams'].extend(json_data)

            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)

            page_num += 1
def pull_epa(year):
    with open('data/teams.json', 'r') as file:
        data = json.load(file)

    keys = [int(team['key'][3:]) for team in data['teams']]

    sb = statbotics.Statbotics()

    all_team_data = []

    for key in keys:
        try:
            team_data = sb.get_team_year(key,year)
            print(team_data)
            all_team_data.append(team_data)
        except UserWarning as e:
            print(f"Warning for team {key}: {e}")
        except Exception as e:
            # catch other unexpected errors
            print(f"Error for team {key}: {e}")

    with open("data/statbotics_data.json", "w") as json_file:
        json.dump(all_team_data, json_file, indent=4)