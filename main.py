import pull_data
import json
import statbotics

pull_data.pull_year(2023)

sb = statbotics.Statbotics()
data = sb.get_team_years()
with open(f"data/statbotics_data.json", "w") as json_file:
   json.dump(data, json_file, indent=4)
print("Done")