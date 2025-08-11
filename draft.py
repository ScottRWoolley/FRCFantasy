import json
import statbotics

def scale_dict_values(data_dict, new_min=1, new_max=50):
    values = list(data_dict.values())
    old_min = min(values)
    old_max = max(values)

    def scale(x):
        # handle edge case if all values are equal
        if old_max == old_min:
            return (new_max + new_min) / 2
        return (x - old_min) / (old_max - old_min) * (new_max - new_min) + new_min

    scaled_dict = {k: scale(v) for k, v in data_dict.items()}
    return scaled_dict

def snake_draft():
    with open('data/statbotics_data.json', 'r') as file:
        teams_data = json.load(file)

    team_epa_dict = {team['team']: team['epa']['breakdown']['total_points'] for team in teams_data}
    scaled_dict = scale_dict_values(team_epa_dict)
    sorted_team_epa_dict = dict(sorted(scaled_dict.items(), key=lambda item: item[1], reverse=True))


    print(sorted_team_epa_dict)

    playern = 10

    snake_draft = {i: [] for i in range(playern)}
    for round_num in range(8):
        print(f"{round_num}:roundN")
        top_teams = list(sorted_team_epa_dict.keys())[:playern]
        if round_num % 2 == 0:
            for i, team in enumerate(top_teams):
                snake_draft[i].append(team)
                sorted_team_epa_dict = {k: v for k, v in sorted_team_epa_dict.items() if k not in top_teams}
        else:
            for i, team in enumerate(reversed(top_teams)):
                snake_draft[i].append(team)
                sorted_team_epa_dict = {k: v for k, v in sorted_team_epa_dict.items() if k not in top_teams}


    with open("data/draft.json", "w") as f:
        json.dump(snake_draft, f, indent=4)