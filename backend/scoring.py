import json
import os
import pull_data

def get_scores(team_key, file_index):
    """
    Reads a JSON file in data/{team_key}/ based on file_index.
    file_index = 0 returns the first file (sorted alphabetically),
    1 returns the second, etc.
    """
    folder_path = f"data/{team_key}"

    json_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".json")])
    if not json_files:
        print(f"No JSON file found for team {team_key} in {folder_path}")
        return []

    if file_index < 0 or file_index >= len(json_files):
        print(f"Invalid file index {file_index}, using first file instead")
        file_index = 0

    file_path = os.path.join(folder_path, json_files[file_index])
    print(f"Using JSON file: {file_path}")

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

def calculate_team_scores(team_list):
    """
    Calculate total scores for each team in team_list.
    Returns a dictionary {team_key: total_score}.
    """
    all_scores = {}

    for team in team_list:
        folder_path = f"data/{team}/"
        json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
        json_number = len(json_files)-1
        total_score = 0
        while json_number != 0:
            scores = get_scores(team,json_number)
            for s in scores:
                match_score = s["ally_score"] + s["rp"]
                total_score += match_score
            json_number -= 1

        all_scores[team] = total_score
        print(f"{team}: Total Score = {total_score}")

    return all_scores



def save_scores_dict(team_list, output_file="data/scores.json"):
    score = calculate_team_scores(team_list)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(score, f, indent=4)