import os

import requests
import json
import datetime
import pandas as pd

club_id = 1110060

week_offset = 1
per_page = None
sort_by = 'moving_time'

headers = {
    'accept': 'text/javascript',
    'x-requested-with': 'XMLHttpRequest'
}

url = f'https://www.strava.com/clubs/{club_id}/leaderboard?{week_offset=}&{per_page=}&{sort_by=}'

# get the last weeks rankings
response = requests.get(url, headers=headers)
response_data = response.json()['data']

# dump new weekly information into file
now = datetime.datetime.now()
file_path = f'weekly_data/{now.year}/data_week_{now:%V}_{now.date()}.json'
os.makedirs(os.path.dirname(file_path), exist_ok=True)
open(file_path, 'w').write(json.dumps(response_data))

# create a leaderboard
leaderboard = {}
for year in os.listdir('weekly_data'):
    week_points = {}
    for week in os.listdir(f'weekly_data/{year}'):
        week_data = json.loads(open(f'weekly_data/{year}/{week}').read())
        for rank, athlete in enumerate(week_data[:3]):
            name = f"{athlete['athlete_firstname']} {athlete['athlete_lastname']};{athlete['athlete_id']}"
            week_points.update({name: week_points.get(name, 0) + 3 - rank})
    leaderboard[year] = week_points

# Create an empty DataFrame
df = pd.DataFrame(columns=['Name'] + list(leaderboard.keys()))

# Populate the DataFrame
for year, values in leaderboard.items():
    for name_id, points in values.items():
        if name_id not in df['Name'].tolist():
            df.loc[len(df)] = [name_id] + [0] * len(leaderboard)
        df.loc[df['Name'] == name_id, year] += points
df = df.sort_values(by=f'{now.year}', ascending=False)

# add a total column
df['Total'] = df.iloc[:, 1:].sum(axis=1)

# add a rank column
df = df.reset_index(drop=True)
df = df.rename_axis('Rang')
df.index += 1

# format the name column
df['Name'] = df['Name'].apply(lambda name_id: "[{}](https://www.strava.com/athletes/{})".format(*name_id.split(';')))

# add emphasis to the current year
current_year = f'{now.year}'
formatted_last_year = df[current_year].apply(lambda x: f'**{x}**')
df = df.drop(current_year, axis=1)
df.insert(len(df.columns) - 1, f'<u>{current_year}</u>', formatted_last_year)

# write leaderboard to the README.md
with open('README.md', 'w', encoding='utf-8') as f:
    f.write('## Rangliste\n\n')
    f.write(df.to_markdown())
