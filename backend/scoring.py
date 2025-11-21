import json
import os
from backend import pull_data
from backend import mongoer

AUTO_WEIGHT = 0.3
TELE_WEIGHT = 0.1
RP_WEIGHT = 0.8
QM_WIN = 2
PLAYOFF_WIN = 2
PLAYOFF_AUTO = 0.3
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
    event_statuses = pull_data.pull_team_statuses(team_key)
    events = []
    for k, e in event_statuses.items():
        events.append(ALL_EVENTS[k])

    events = sorted(events, key=convert_date_to_int)
    #valid_events = list(filter(lambda e: e["event_type"] != 99, events))
    valid_events = events

    # first_2 = []
    # last = []
    # mult_events = []
    # if len(valid_events) >= 2:
    #     first_2 = valid_events[0:1]
    #     if len(valid_events) > 2:
    #         last = [valid_events[-1]]
    #         if len(valid_events) > 3:
    #             mult_events = valid_events[2:-2]
    # valid_events = first_2 + last

    events = list(map(lambda e: e["key"], events))
    valid_events = list(map(lambda e: e["key"], valid_events))

    total = 0.0

    for event in valid_events:
        comp_matches = list(filter(lambda m: m["event_key"] == event, matches))
        total += get_team_event_score(team_key, event, event_statuses[event], comp_matches)

    return round(total, 2)

def get_team_event_score(team, event_key, event_status, event_matches):
    total = 0.0

    for match in event_matches:
        try:
            alliances = match["alliances"]

            if team in alliances["red"]["team_keys"]:
                side = "red"
            elif team in alliances["blue"]["team_keys"]:
                side = "blue"
            else:
                continue

            total += calculate_match_score(match, side)

        except Exception:
            continue
    
    total += calc_event_playoff_bonus(event_key, event_status)

    return round(total, 2)


def calculate_team_scores(teams):
    team_scores = dict.fromkeys(teams, 0)
    for team in teams:
        total_score = get_scores(team)
        team_scores[team] = total_score

    return team_scores


def save_scores_dict(scorelist):
    data = mongoer.find("scores")[0]
    new_data = data | scorelist
    mongoer.update_document("scores", query={"_id": data["_id"]}, new_data=new_data)


def add_score_from_match(tim_scores, teams):
    data = mongoer.find("scores")[0]
    for team in teams:
        data[team] += tim_scores[team]
    mongoer.update_document("scores", query={"_id": data["_id"]}, new_data=data)


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
        return 0
        #return calculate_playoff_score(match, color)

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
    all_teams = mongoer.find("all_teams")[0]["data"]
    
    scores = calculate_team_scores(all_teams)
    save_scores_dict(scores)

def update_teams(teams, match):
    all_teams = mongoer.find("all_teams")[0]["data"]
    
    t = list(set(all_teams).intersection(set(teams)))
    tim_scores = calc_tim_scores(match)
    add_score_from_match(tim_scores, t)
    return tim_scores

def calc_event_playoff_bonus(key, event):
    total = 0
    last_round = {
        "r1": ["sf1m1", "sf2m1", "sf3m1", "sf4m1", "sf5m1", "sf6m1"],
        "r2": ["sf7m1", "sf8m1", "sf9m1", "sf10m1"],
        "r3": ["sf11m1", "sf12m1"],
        "r4": ["sf13m1"],
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
        return 0
    total += round_values[r]
    if event["playoff"]["status"] == "won":
        total += COMP_WIN_BONUS
    return total

def convert_date_to_int(e):
    return int(e["start_date"].replace("-", ""))