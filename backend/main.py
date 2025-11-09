import pull_data
import scoring
import json
import send


def read_team_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

teamlist = ["frc1678","frc8768","frc6662","frc254"]
# for team in teamlist:
#     pull_data.event(team,"2025cada")
#     scores = scoring.get_scores(f"data/{team}/2025cada.json", team)
#     score = 0
#     for s in scores:
#         matchscore = (s["ally_score"]) + (s["rp"])
#         score += matchscore
#         #print(f"{s['match_key']}: {devide} for {team}")
#     print(f"{score} for {team}")


scoring.save_scores_dict(teamlist,"2025cada")


x = send.score("1436951442937090180")

print(x)



print("Done")