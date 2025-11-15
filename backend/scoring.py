import json
import os
from backend import pull_data

def get_scores(team_key):
    matches = pull_data.pull_team_matches(team_key)

    total = 0.0

    for match in matches:
        try:
            if match.get("comp_level") != "qm":
                continue
            alliances = match["alliances"]

            if team_key in alliances["red"]["team_keys"]:
                side = "red"
            elif team_key in alliances["blue"]["team_keys"]:
                side = "blue"
            else:
                continue

            total += calculate_match_score(match, side)

        except Exception:
            continue

    return round(total, 2)

def calculate_team_scores(teams):
    team_scores = dict.fromkeys(teams, 0)
    for team in teams:
        total_score = get_scores(team)
        team_scores[team] = total_score

    return team_scores


def save_scores_dict(scorelist, output_file="scores.json"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "r") as f:
        data = json.load(f)
    new_data = data | scorelist
    with open(output_file, "w") as f:
        json.dump(new_data, f)


def calculate_match_score(match, color):
    breakdown = match.get("score_breakdown", {})
    if not breakdown:
        return match["alliances"][color]["score"] * 0.1
    winning = match.get("winning_alliance")

    auto_score = breakdown[color]["autoPoints"]
    tele_points = breakdown[color]["teleopPoints"]
    rp = breakdown[color]["rp"]
    win = 1 if winning == color else 0

    # weighted formula
    weighted_score = (auto_score * 0.15) + (tele_points * 0.10) + (rp * 0.80) + win
    return round(weighted_score, 2)

def calc_tim_scores(match):
    alliances = match["alliances"]
    scores = {}
    for color in ["blue", "red"]:
        alliance_score = calculate_match_score(match, color)
        teams = alliances[color]["teams"]
        for team in teams:
            scores[team] = alliance_score
    return scores

def calc_all_teams():
    with open("all_teams.json", "r") as f:
        all_teams = json.load(f)
    
    scores = calculate_team_scores(all_teams)
    save_scores_dict(scores)


def update_teams(teams, match):
    with open("all_teams.json", "r") as f:
        all_teams = json.load(f)
    
    t = set(all_teams).intersection(set(teams))
    scores = calculate_team_scores(list(t))
    save_scores_dict(scores)
    tim_scores = calc_tim_scores(match)
    return tim_scores