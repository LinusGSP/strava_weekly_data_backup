import datetime
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

# load environment variables
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')
club_id = os.getenv('CLUB_ID')

# create a session
session = requests.Session()
session.headers.update({
    'accept': 'text/javascript',
    'x-requested-with': 'XMLHttpRequest'
})

# get an authenticity token
response_text = session.get('https://www.strava.com/login').text
authenticity_token = response_text.split('name="authenticity_token" value="')[1].split('"')[0]

login_data = {
    'email': email,
    'password': password,
    'authenticity_token': authenticity_token,
    'utf8': '✓'
}

# login
login_url = 'https://www.strava.com/session'
login_response = session.post(login_url, data=login_data)
if login_response.status_code != 200:
    print('Login failed')
    exit(1)

url = f'https://www.strava.com/clubs/{club_id}/leaderboard?week_offset=1&per_page=None&sort_by=moving_time'
now = datetime.datetime.now()
current_year = f'{now.year}'

# get the last weeks rankings
response = session.get(url)
print(response.content)
response_data = response.json()['data']

# dump new weekly information into file
file_path = f'weekly_data/{current_year}/data_week_{now:%V}_{now.date()}.json'
os.makedirs(os.path.dirname(file_path), exist_ok=True)
open(file_path, 'w').write(json.dumps(response_data))

# create a dataframe with the weekly data
data = list(sorted(os.listdir('weekly_data'), reverse=True))
df = pd.DataFrame(columns=['Name', *data])
for year in data:
    for week in os.listdir(f'weekly_data/{year}'):
        week_data = json.loads(open(f'weekly_data/{year}/{week}').read())
        for rank, athlete in enumerate(week_data[:3]):
            name = f"{athlete['athlete_firstname']} {athlete['athlete_lastname'][0]}.;{athlete['athlete_id']}"
            if name not in df['Name'].tolist():
                df.loc[len(df)] = [name] + [0] * len(data)
            df.loc[df['Name'] == name, year] += 3 - rank
df = df.sort_values(by=list(df.columns[1:]), ascending=[False] * (len(df.columns) - 1))

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
