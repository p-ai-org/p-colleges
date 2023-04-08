import os
import json

directory = "/Users/hmcuser/Desktop/p-colleges/Brian/Rate My Professor"

combined_data = {}

for filename in os.listdir(directory):
    if filename.endswith(".json"):
        with open(os.path.join(directory, filename)) as f:
            json_data = json.load(f)

        combined_data.update(json_data)

with open("all_colleges_RMP_COMBINED.json", "w") as f:
    json.dump(combined_data, f, indent=4)
