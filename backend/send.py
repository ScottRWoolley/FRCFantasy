import json
from backend import scoring
import requests
import os
from backend import mongoer
import copy
import asyncio
from tba_requests import tba_request

EMOJIS = [":arrow_double_down:", ":arrow_down_small:", ":heavy_minus_sign:", ":arrow_up_small:", ":arrow_double_up:"]

def score(channel_id): 
    result = {}
    
    scores = mongoer.find("scores")[0]
    
    users = mongoer.find("bible", {"server_id": channel_id})[0]["players"]
    for username, teams in users.items():
        if username not in result:
            result[username] = {}
        for team in teams:
            result[username][team] = scores[team]
    """{
        'scott': {
            'frc1678': 1,
        },
    }"""
    return result

async def pull_match_score(match_key):
    await asyncio.sleep(60)

    match_data = tba_request(f"/match/{match_key}")
    

def send_score_updates(teams, match):
    scores = scoring.update_teams(teams, match)

    webhook_urls = mongoer.find("webhook_urls")[0]
    del webhook_urls["_id"]
    
    for serverid, url in webhook_urls.items():
        intersecting_teams = []
        previous_scores = score(serverid)
        new_scores = copy.deepcopy(previous_scores)

        for user, user_teams in new_scores.items():
            if intersect := set(user_teams.keys()).intersection(set(teams)):
                intersecting_teams += list(intersect)
                for t in intersect:
                    previous_scores[user][t] -= scores[t]

        if len(intersecting_teams) > 0:
            message = f"SCORE UPDATE!!! ({match["key"]})\n"
            for team in intersecting_teams:
                message += f"{team[3:]} scored {scores[team]}\n"
            
            sorted_score = sorted(new_scores.keys(), key = lambda k: sum(new_scores[k].values()), reverse=True)
            previous_sorted_score = sorted(previous_scores.keys(), key = lambda k: sum(previous_scores[k].values()), reverse=True)

            for player in sorted_score:
                message += add_dashes_until_length(f"{player}: {round(sum(new_scores[player].values()), 2)}", 30)
                message += leaderboard_change(sorted_score, previous_sorted_score, player)
                message += "\n"

            send_webhook(message, url)

def leaderboard_change(previous, new, item):
    new_index = new.index(item)
    previous_index = previous.index(item)
    change = new_index-previous_index
    if change > 1:
        return EMOJIS[4]
    elif change == 1:
        return EMOJIS[3]
    elif change == 0:
        return EMOJIS[2]
    elif change == -1:
        return EMOJIS[1]
    else:
        return EMOJIS[0]

def add_dashes_until_length(string, length):
    strlength = len(string)
    return string + "-" * (length - strlength) 

def send_webhook(message, url):
    response = requests.post(url, data=json.dumps({"content": message}), headers={"Content-Type": "application/json"})
    if response.status_code == 204:
        return True
    else:
        print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
        return False