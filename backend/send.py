import json
from backend import pull_data
from backend import scoring

file_path = "bible.json"
score_file_path = "data/scores.json"

def score(channel_id):
    result = {}

    with open(file_path, "r") as f:
        data = json.load(f)
    
    for msg_id, users in data.items():
        if msg_id == channel_id:
            for username, teams in users.items():
                pull_data.pull_teams(teams)
                scoring.save_scores_dict(teams)
                with open(score_file_path, "r") as f:
                    scores = json.load(f)
                if username not in result:
                    result[username] = {}
                for team in teams:
                    result[username][team] = scores[team]
    return result

