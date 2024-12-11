'''Test script to get tests from HDForce API'''
import os
import time
import datetime
from hdforce import AuthManager
import hdforce as hd
from dotenv import load_dotenv

load_dotenv()

AuthManager(
    region='Americas',
    authMethod='env',
    refreshToken_name='HD_REFRESH_TOKEN',
    refreshToken=os.getenv('HD_REFRESH_TOKEN')
)

hdTeams = hd.GetTeams()
teamID = hdTeams.loc[hdTeams['name'] == 'Football']['id'].values[0]
print(teamID)

def epoch_time(month, day, year):
    '''Function to convert a date to epoch time'''
    return int(time.mktime(datetime.datetime(year, month, day).timetuple()))

#get the tests in chunks by year
for eachYear in range(2021, 2024):
    #create function to convert to epoch time
    fromTime = epoch_time(1, 1, eachYear)
    toTime = epoch_time(1, 1, eachYear+1)
    print(fromTime, toTime)
    tests = hd.GetTests(teamId= teamID, from_=fromTime, to_=toTime)
    print(tests)
