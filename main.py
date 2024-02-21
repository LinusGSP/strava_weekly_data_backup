import os

import requests
import json
import datetime
import pandas as pd

club_id = 1110060

headers = {
    'accept': 'text/javascript',
    'x-requested-with': 'XMLHttpRequest'
}

url = f'https://www.strava.com/clubs/{club_id}/leaderboard?week_offset=1&per_page=None&sort_by=moving_time'

now = datetime.datetime.now()
current_year = f'{now.year}'

# get the last weeks rankings
response = requests.get(url, headers=headers)
response_data = response.json()['data']

# dump new weekly information into file
file_path = f'weekly_data/{current_year}/data_week_{now:%V}_{now.date()}.json'
os.makedirs(os.path.dirname(file_path), exist_ok=True)
open(file_path, 'w').write(json.dumps(response_data))

# create a dataframe with the weekly data
data = list(reversed(os.listdir('weekly_data')))
df = pd.DataFrame(columns=['Name', *data])
for year in data:
    for week in os.listdir(f'weekly_data/{year}'):
        week_data = json.loads(open(f'weekly_data/{year}/{week}').read())
        for rank, athlete in enumerate(week_data[:3]):
            name = f"{athlete['athlete_firstname']} {athlete['athlete_lastname']};{athlete['athlete_id']}"
            if name not in df['Name'].tolist():
                df.loc[len(df)] = [name] + [0] * len(data)
            df.loc[df['Name'] == name, year] += 3 - rank
df = df.sort_values(by=list(df.columns[:0:-1]), ascending=[False] * (len(df.columns) - 1))

# add a total column
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
