import pull_data as pull_data
import json
import statbotics
import scoring as scoring

#pull_data.pull_year(2023)

#pull_data.pull_epa(2023)

#draft.snake_draft()

teamlist = ["frc1678","frc8768","frc6662","frc254"]
for team in teamlist:
    pull_data.event(team,"2025cada")
    scores = scoring.get_scores("data/teamincomp.json", team)
    score = 0
    for s in scores:
        matchscore = (s["ally_score"]) + (s["rp"])
        score += matchscore
        #print(f"{s['match_key']}: {devide} for {team}")
    print(f"{score} for {team}")




print("Done")