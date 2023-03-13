import os

import requests
import json
import datetime
import pandas as pd

week_offset = 1
per_page = None
sort_by = 'moving_time'

headers = {
    'accept': 'text/javascript',
    'referer': 'https://www.strava.com/clubs/1110060',
    'x-requested-with': 'XMLHttpRequest'
}

url = f'https://www.strava.com/clubs/1110060/leaderboard?{week_offset=}&{per_page=}&sort_by={sort_by}'

# get the last weeks data
response = requests.get(url, headers=headers)
data: list = response.json()['data']

# create directory if not exists
if not os.path.exists('weekly_data'):
    os.makedirs('weekly_data')

# dump new weekly information into folder
file_name = f'weekly_data/data_week_{datetime.datetime.now():%V}_{datetime.datetime.now().date()}.json'

if os.path.exists(file_name):
    print("Already collected data for this week.")
    exit()

with open(file_name, 'w') as f:
    json.dump(data, f)

# create the leaderboard if not exists
if not os.path.exists('leaderboard.json'):
    with open('leaderboard.json', 'w') as f:
        json.dump({}, f)

# load the old leaderboard
with open('leaderboard.json', 'r') as f:
    leaderboard: dict = json.load(f)

# add new top 3 to leaderboard
for i, p in enumerate(data[:3]):
    name: str = f"{p['athlete_firstname']} {p['athlete_lastname']};{p['athlete_id']}"

    if leaderboard.__contains__(name):
        leaderboard[name] += 3 - i
    else:
        leaderboard[name] = 3 - i


print(leaderboard)

# safe the new leaderboard
with open('leaderboard.json', 'w') as f:
    json.dump(leaderboard, f)

# safe the new markdown file
leaderboard_data = [(points, name.split(';')[0]) for (name, points) in leaderboard.items()]
leaderboard_data.sort(key=lambda x: x[0], reverse=True)  # sort by points

df = pd.DataFrame(leaderboard_data, columns=('Punkte', 'Name'))
with open('README.md', 'w') as f:
    f.write('## Rangliste\n\n')
    f.write(df.to_markdown())
