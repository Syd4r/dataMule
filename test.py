from hdforce import AuthManager
import hdforce as hd
import os
from dotenv import load_dotenv

load_dotenv()

AuthManager(
    region='Americas',
    authMethod='env',
    refreshToken_name='HD_REFRESH_TOKEN',
    refreshToken=os.getenv('HD_REFRESH_TOKEN')
)

team_name = 'Football'
hd_teams = hd.GetTeams()
team_id = hd_teams.loc[hd_teams['name'] == team_name]['id'].values[0]
print(team_id)

def epoch_time(month, day, year):
    import time
    import datetime
    return int(time.mktime(datetime.datetime(year, month, day).timetuple()))

#get the tests in chunks by year
for year in range(2021, 2024):
    #create function to convert to epoch time
    from_time = epoch_time(1, 1, year)
    to_time = epoch_time(1, 1, year+1)
    print(from_time, to_time)
    tests = hd.GetTests(teamId= team_id, from_=from_time, to_=to_time)
    print(tests)