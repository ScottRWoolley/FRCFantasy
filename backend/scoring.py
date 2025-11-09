import json

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
