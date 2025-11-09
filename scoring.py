import json
import sys

class Team:
    def __init__(self, team_id):
        self.team_id = team_id
        self.score = 0
        self.events = []
        self.wins = 0
        self.losses = 0
        self.n_events = 0
    
    def add_score(self, points):
        self.score += points
    
    def get_score(self):
        return self.score
    
    def add_event(self, event_name):
        if event_name not in self.events:  # avoid duplicates
            self.events.append(event_name)
            self.n_events += 1
    def add_event_count(self):
        self.n_events += 1

    def get_events(self):
        return self.events
    
    def get_n_events(self):
        return self.n_events


# Load data
with open('data/teams.json', 'r') as file:
    teamdata = json.load(file)

with open('data/comps.json', 'r') as file:
    data = json.load(file)

number = 0
comlen = len(data["comps"])
teams = {}  # dict to hold Team objects

for team_info in teamdata['teams']:
    key = team_info["key"]
    teams[key] = Team(key)

for event in data["comps"]:
    event_key = event["key"]
    if event["event_type"] == 0:
        number += 1
        print(event_key)

        with open(f'data/matches/{event_key}.json', 'r') as file:
            matchdata = json.load(file)  # matches + other info
        #sys.stdout.write(f"\rScoring Games {number}/{comlen} Name {event_key}")
        #sys.stdout.flush()

        # Score the matches
        for match in matchdata['matches']:
            cl = match["comp_level"]
            if cl == "qm":
                blue_alliance = match["alliances"]["blue"]
                red_alliance = match["alliances"]["red"]

                if match["winning_alliance"] == "blue":
                    point = blue_alliance["score"]
                    for team in blue_alliance['team_keys']:
                        team_num = team[3:]
                        if team_num.isdigit():
                            if event_key not in teams[team].get_events():
                                teams[team].add_event(event_key)
                            if teams[team].get_n_events() < 3:
                                teams[team].add_score(point)

                if match["winning_alliance"] == "red":
                    point = red_alliance["score"]
                    for team in red_alliance['team_keys']:
                        team_num = team[3:]
                        if team_num.isdigit():
                            if event_key not in teams[team].get_events():
                                teams[team].add_event(event_key)
                            if teams[team].get_n_events() < 3:
                                teams[team].add_score(point)

# Sort by score ascending, remove 0-score teams
sorted_teams = sorted(
    [t for t in teams.values() if t.get_score() > 0],
    key=lambda t: t.get_score(),
    reverse=False
)

# Build final dict
final_scores = {
    team.team_id: {
        "score": team.get_score(),
        "events": team.get_events()
    }
    for team in sorted_teams
}

print(final_scores)
