

"""Example json element
    {
        "date": "2025-01-02",
        "podium": [
            "Vroni Steinmann",
            "Sepp Fuchs",
            "Silvia Purga"
        ]
    },
"""

# filename: data.json

import json


def load_data(filename):
    with open(filename, 'r', encoding='UTF-8') as file:
        data = json.load(file)
    return data

# print out (unique) names ordered by name

data = load_data('data.json')

names = set()
for entry in data:
    for name in entry['podium']:
        names.add(name)
for name in sorted(names):
    print(name)



# for a first place you get 3 points, for a second place 2 points and for a third place 1 point
points = {}
for entry in data:
    podium = entry['podium']
    points[podium[0]] = points.get(podium[0], 0) + 3
    points[podium[1]] = points.get(podium[1], 0) + 2
    points[podium[2]] = points.get(podium[2], 0) + 1

# print out the names and their points ordered by points
sorted_points = sorted(points.items(), key=lambda x: x[1], reverse=True)
for name, point in sorted_points:
    print(f"{name}: {point} points")
