import json
import os
from backend import pull_data

AUTO_WEIGHT = 0.15
TELE_WEIGHT = 0.1
RP_WEIGHT = 0.8
QM_WIN = 1
PLAYOFF_WIN = 2
PLAYOFF_AUTO = 0.15
PLAYOFF_TELE = 0.1
R1 = 10
R2 = 20
R3 = 40
R4 = 60
R5 = 80
COMP_WIN_BONUS = 20

with open("jsons/all_events.json", "r") as f:
    ALL_EVENTS = json.load(f)

def get_scores(team_key):
    matches = pull_data.pull_team_matches(team_key)

    total = 0.0

    for match in matches:
        if ALL_EVENTS[match["event_key"]]["event_type"] == 99:
            continue
        try:
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
    
    total += calc_playoff_bonus(team_key)

    return round(total, 2)

def calculate_team_scores(teams):
    team_scores = dict.fromkeys(teams, 0)
    for team in teams:
        total_score = get_scores(team)
        team_scores[team] = total_score

    return team_scores


def save_scores_dict(scorelist, output_file="scores.json"):
    with open(output_file, "r") as f:
        data = json.load(f)
    new_data = data | scorelist
    with open(output_file, "w") as f:
        json.dump(new_data, f)


def calculate_qm_score(match, color):
    breakdown = match.get("score_breakdown", {})
    if not breakdown:
        return round(match["alliances"][color]["score"] * TELE_WEIGHT, 2)
    winning = match.get("winning_alliance")

    auto_score = breakdown[color]["autoPoints"]
    tele_points = breakdown[color]["teleopPoints"]
    rp = breakdown[color]["rp"]
    win = QM_WIN if winning == color else 0

    # weighted formula
    weighted_score = (auto_score * AUTO_WEIGHT) + (tele_points * TELE_WEIGHT) + (rp * RP_WEIGHT) + win
    return round(weighted_score, 2)


def calculate_playoff_score(match, color):
    breakdown = match.get("score_breakdown", {})
    if not breakdown:
        return round(match["alliances"][color]["score"] * PLAYOFF_TELE, 2)
    winning = match.get("winning_alliance")

    auto_score = breakdown[color]["autoPoints"]
    tele_points = breakdown[color]["teleopPoints"]
    win = PLAYOFF_WIN if winning == color else 0

    # weighted formula
    weighted_score = (auto_score * PLAYOFF_AUTO) + (tele_points * PLAYOFF_TELE) + win
    return round(weighted_score, 2)

def calculate_match_score(match, color):
    if match["comp_level"] == "qm":
        return calculate_qm_score(match, color)
    else:
        return calculate_playoff_score(match, color)

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
    with open("jsons/all_teams.json", "r") as f:
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

def calc_playoff_bonus(team_key):
    total = 0
    events = pull_data.pull_team_statuses(team_key)
    
    for key, event in events.items():
        if ALL_EVENTS[key]["event_type"] == 99:
            continue
        last_round = {
            "r1": ["sfm1", "sfm2", "sfm3", "sfm4", "sfm5", "sfm6"],
            "r2": ["sfm7", "sfm8", "sfm9", "sfm10"],
            "r3": ["sfm11", "sfm12"],
            "r4": ["sfm13"],
            "r5": ["f1m1", "f1m2", "f1m3"]
        }
        round_values = {
            "r1": R1,
            "r2": R2,
            "r3": R3,
            "r4": R4,
            "r5": R5
        }
        last_key = event["last_match_key"]
        r = [last_r for last_r, keys in last_round.items() if last_key.replace(f"{key}_", "") in keys]
        if len(r) > 0:
            r = r[0]
        else:
            continue
        total += round_values[r]
        if event["playoff"]["status"] == "won":
            total += COMP_WIN_BONUS



    return total