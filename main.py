import datetime
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

# load environment variables
session_token = os.getenv('SESSION_TOKEN')
club_id = os.getenv('CLUB_ID')

# create a session
session = requests.Session()
session.headers.update({
    'accept': 'text/javascript',
    'x-requested-with': 'XMLHttpRequest',
    'cookie': f'_strava4_session={session_token}',
})

url = f'https://www.strava.com/clubs/{club_id}/leaderboard?week_offset=1&per_page=None&sort_by=moving_time'
now = datetime.datetime.now()
current_year = f'{now.year - 1}'

"""
# get the last weeks rankings
response = session.get(url)
print(response.content)
response_data = response.json()['data']

# dump new weekly information into file
file_path = f'weekly_data/{current_year}/data_week_{now:%V}_{now.date()}.json'
os.makedirs(os.path.dirname(file_path), exist_ok=True)
open(file_path, 'w').write(json.dumps(response_data))
"""
# create a dataframe with the weekly data
dirs = list(sorted(os.listdir('weekly_data'), reverse=True))
df = pd.DataFrame(columns=['Name', *dirs])
for year in ["2023", "2024"]:
    for week in os.listdir(f'weekly_data/{year}'):
        week_data = json.loads(open(f'weekly_data/{year}/{week}').read())
        for rank, athlete in enumerate(week_data[:3]):
            name = f"{athlete['athlete_firstname']} {athlete['athlete_lastname'][0]}.;{athlete['athlete_id']}"
            if name not in df['Name'].tolist():
                # use number of dataframe value-columns (exclude 'Name') to avoid mismatched columns
                df.loc[len(df)] = [name] + [0] * (len(df.columns) - 1)
            df.loc[df['Name'] == name, year] += 3 - rank
df = df.sort_values(by=list(df.columns[1:]), ascending=[False] * (len(df.columns) - 1))

"""
load data.json
[
    {
        "date": "2025-01-02",
        "podium": [
            "Vroni Steinmann",
            "Sepp Fuchs",
            "Silvia Purga"
        ]
    },
    ...
    ]
"""

"""
load user_mapping.json
[
 { "user": "Sepp Fuchs", "id": 16756310 },
{ "user": "Nalinakumar INDIA", "id": 138394824 },
...
]
"""
directory = "weekly_data/2025/"

with open(directory + 'data.json', 'r', encoding='UTF-8') as file:
    entries = json.load(file)

with open(directory + 'user_mapping.json', 'r', encoding='UTF-8') as file:
    user_mapping = json.load(file)

for entry in entries:
    podium = entry['podium']
    for rank, name in enumerate(podium):
        user_id = next((user['id'] for user in user_mapping if user['user'] == name), None)
        if user_id is None:
            print(f"User {name} not found in user_mapping.json")
            continue

        # find the name_id by searching for the user_id in the existing dataframe at the end, if not found create a new entry
        name_id = df[df['Name'].str.contains(f';{user_id}$')]['Name'].values
        if len(name_id) == 0:
            name_id = f"{name};{user_id}"
            df.loc[len(df)] = [name_id] + [0] * (len(df.columns) - 1)
        else:
            name_id = name_id[0]
        df.loc[df['Name'] == name_id, current_year] += 3 - rank

df = df.sort_values(by=list(df.columns[1:]), ascending=[False] * (len(df.columns) - 1))

df[''] = None
df['Total'] = df.iloc[:, 1:].sum(axis=1)

# add a rank column
df = df.reset_index(drop=True)
df = df.rename_axis('Rang')
df.index += 1

# format the name column to be a Markdown link to the profile
df['Name'] = df['Name'].apply(lambda name_id: "[{}](https://www.strava.com/athletes/{})".format(*name_id.split(';')))

# add emphasis to the current year
df[current_year] = df[current_year].apply(lambda x: f'**{x}**')

# write leaderboard to the README.md
with open('README.md', 'w', encoding='utf-8') as f:
    f.write('## Rangliste\n\n')
    f.write(df.to_markdown())
