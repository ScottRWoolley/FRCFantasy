import json
import os
import pull_data

def get_scores(team_key, comp):
    file_path = f"data/{team_key}/{comp}.json"

    with open(file_path, "r") as f:
        matches = json.load(f)

    scores = []

    for match in matches:
        try:
            alliances = match["alliances"]
            breakdown = match.get("score_breakdown", {})

            if team_key in alliances["red"]["team_keys"]:
                side = "red"
                other = "blue"
            elif team_key in alliances["blue"]["team_keys"]:
                side = "blue"
                other = "red"
            else:
                continue

            ally_score = alliances[side]["score"]
            opponent_score = alliances[other]["score"]

            side_breakdown = breakdown.get(side, {})
            rp = (
                side_breakdown.get("rp") or
                side_breakdown.get("ranking_points") or
                side_breakdown.get("bonus_rp") or
                0
            )

            scores.append({
                "match_key": match.get("key", "unknown"),
                "ally_score": ally_score,
                "opponent_score": opponent_score,
                "rp": rp
            })
        except KeyError:
            continue

    return scores

def calculate_team_scores(team, event):

    folder_path = f"data/{team}/"
    total_score = 0
    scores = get_scores(team, event)
    for s in scores:
        match_score = s["ally_score"] + s["rp"]
        total_score += match_score

    print(f"{team}: Total Score = {total_score}")

    return total_score



def save_scores_dict(scorelist, output_file="data/scores.json"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(scorelist, f, indent=4)