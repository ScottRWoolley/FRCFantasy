import pull_data
import draft
import json
import statbotics

#pull_data.pull_year(2023)

#pull_data.pull_epa(2023)

#draft.snake_draft()

pull_data.pull_comps(2023)

with open('data/comps.json', 'r') as file:
    data = json.load(file)

for event in data["comps"]:
    if event["event_type"] == 0:
        event_key = event["key"]   # extract the key
        print(f"pulling {event_key}")
        pull_data.pull_matches(event_key)



print("Done")