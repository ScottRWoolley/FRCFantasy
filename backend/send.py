import json
from backend import scoring
import requests
import os
from backend import mongoer

def score(channel_id): 
    result = {}
    
    scores = mongoer.find("scores")[0]
    
    users = mongoer.find("bible", {"server_id": channel_id})[0]["players"]
    for username, teams in users.items():
        if username not in result:
            result[username] = {}
        for team in teams:
            result[username][team] = scores[team]
    return result

def send_score_updates(teams, match):
    scores = scoring.update_teams(teams, match)

    webhook_urls = mongoer.find("webhook_urls")[0]
    
    for serverid, url in webhook_urls.items():
        server_bible = mongoer.find("bible", {"server_id": serverid})
        intersecting_teams = set(scores.keys()).intersection(set(sum(server_bible.values(), [])))
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