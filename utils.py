import json

def update_json(file_path, data):
    with open(file_path, "r") as f:
        file_data = json.load(f)

    if isinstance(data, dict):
        file_data.update(data)
        print(file_data)
    elif isinstance(data, list):
        file_data.extend(data)

    with open(file_path, "w") as f:
        json.dump(file_data, f)