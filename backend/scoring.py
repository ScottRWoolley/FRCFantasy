import json
import os
import pull_data

def get_scores(file_path, team_key):
    with open(file_path, "r") as f:
        matches = json.load(f)

    scores = []

    for match in matches:
        try:
            alliances = match["alliances"]
            breakdown = match.get("score_breakdown", {})

            # Determine if this team is red or blue
            if team_key in alliances["red"]["team_keys"]:
                side = "red"
                other = "blue"
            elif team_key in alliances["blue"]["team_keys"]:
                side = "blue"
                other = "red"
            else:
                continue  # not in this match

            ally_score = alliances[side]["score"]
            opponent_score = alliances[other]["score"]

            # Try to find RP value (different years name it differently)
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

def calculate_team_scores(team_list, event_key):
    """
    Calculate total scores for each team in team_list.
    Returns a dictionary {team_key: total_score}.
    """
    all_scores = {}

    for team in team_list:
        # Pull event data
        pull_data.event(team, event_key)

        # Get match scores
        file_path = f"data/{team}/{event_key}.json"
        if not os.path.exists(file_path):
            print(f"No data for {team}, skipping.")
            continue

        scores = get_scores(file_path, team)

        # Calculate total score for this team
        total_score = 0
        for s in scores:
            match_score = s["ally_score"] + s["rp"]
            total_score += match_score

        all_scores[team] = total_score
        print(f"{team}: Total Score = {total_score}")

    return all_scores



def save_scores_dict(team_list, event_key, output_file="data/scores.json"):
    score = calculate_team_scores(team_list,event_key)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(score, f, indent=4)
    print(f"Saved all teams' total scores to {output_file}")