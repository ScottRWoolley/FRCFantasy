from backend import pull_data
from backend import scoring
import json
import send
import os

year = "2026"

teamlist = ["frc1678","frc8768","frc6662","frc254"]

scores = scoring.calculate_team_scores(teamlist)

scoring.save_scores_dict(scores)

#pull_data.pull_teams(teamlist)
#scoring.save_scores_dict(teamlist)

#print(send.score("1436951442937090180"))
print("Done")