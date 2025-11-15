import requests
import json

url = f"https://www.thebluealliance.com/api/v3/teams/2026/"
api_key = 'gdMGUFHnD8igdevFP5RZOKIFtFAiupOuhBIPMIrw3jpsQgYlA74wKU5uOnThpQ2V'  
headers = { 'X-TBA-Auth-Key': api_key }
teams = []
index = 0
while True:
    response = requests.get(url + str(index)+ "/keys", headers=headers)
    response = response.json()
    print(index)
    if len(response) == 0:
        break
    else:
        teams.extend(response)
        index += 1
teams = list(map(lambda x: x[3:], teams))
with open("jsons/team_keys.json", "w") as f:
    json.dump(teams, f)