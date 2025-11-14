import json
import os

def get_scores(team_key, comp):
    file_path = f"data/{team_key}/{comp}.json"

    with open(file_path, "r") as f:
        matches = json.load(f)

    total = 0.0

    for match in matches:
        try:
            if match.get("comp_level") != "qm":
                continue
            alliances = match["alliances"]
            breakdown = match.get("score_breakdown", {})
            winning = match.get("winning_alliance")

            if team_key in alliances["red"]["team_keys"]:
                side = "red"
            elif team_key in alliances["blue"]["team_keys"]:
                side = "blue"
            else:
                continue

            auto_score = breakdown[side]["autoPoints"]
            total_points = breakdown[side]["totalPoints"]
            rp = breakdown[side]["rp"]
            win = 1 if winning == side else 0

            # weighted formula
            weighted_score = (auto_score * 0.15) + (total_points * 0.10) + (rp * 0.80) + win
            total += weighted_score

        except Exception:
            continue

    return round(total, 2)

def calculate_team_scores(team, event):

    folder_path = f"data/{team}/"
    total_score = get_scores(team, event)

    print(f"{team}: Total Score = {total_score}")

    return total_score



def save_scores_dict(scorelist, output_file="data/scores.json"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(scorelist, f, indent=4)