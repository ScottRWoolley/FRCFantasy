import json
from backend import scoring
import requests

file_path = "bible.json"
score_file_path = "data/scores.json"

def score(channel_id): 
    result = {}
    with open(file_path, "r") as f:
        data = json.load(f)
    
    with open(score_file_path, "r") as f:
        scores = json.load(f)
    
    users = data[channel_id]
    for username, teams in users.items():
        if username not in result:
            result[username] = {}
        for team in teams:
            result[username][team] = scores[team]
    return result

def send_score_updates(teams, match):
    scores = scoring.update_teams(teams, match)

    with open("webhook_urls.json", "r") as f:
        webhook_urls = json.load(f)
    with open("bible.json", "r") as f:
        bible = json.load(f)
    
    for serverid, url in webhook_urls.items():
        intersecting_teams = set(scores.keys()).intersection(set(sum(bible[serverid].values(), [])))
        if len(intersecting_teams) > 0:
            message = "SCORE UPDATE!!!"
            for team in intersecting_teams:
                message += f"\n{team[3:]} scored {scores[team]}"
            send_webhook(message, url)

def send_webhook(message, url):
    response = requests.post(url, data=json.dumps({"content": message}), headers={"Content-Type": "application/json"})
    if response.status_code == 204:
        return True
    else:
        print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
        return False