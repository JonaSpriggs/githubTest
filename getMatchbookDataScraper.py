
from asyncio import gather
from time import *
from datetime import datetime, timedelta
from dateutil.parser import parse

import requests
import json


def getSport(sport_id):
    if(sport_id == 1 or sport_id == 2):
        return "American Football"
    elif(sport_id == 3):
        return "Baseball"
    elif(sport_id == 4 or sport_id == 5):
        return "Basketball"
    elif(sport_id == 15):
        return "Football"
    
def converted_time_to_epoch(hours_ahead):
    time_cutoff = datetime.now() + timedelta(hours=hours_ahead)
    ts = (time_cutoff - datetime(1970,1,1)).total_seconds()
    date = str(ts)
    full_stop = '.'
    stripped_date = date.split(full_stop, 1)[0]

    return stripped_date
    

url = "https://api.matchbook.com/edge/rest/events?offset=0&per-page=400&sport-ids=3%2C15%2C1%2C6%2C9%2C4&states=open%2Csuspended%2Cclosed%2Cgraded&exchange-type=back-lay&odds-type=DECIMAL&include-prices=false&price-depth=3&price-mode=expanded&include-event-participants=false&exclude-mirrored-prices=false&before=" + converted_time_to_epoch(72)

def convertTime(time):
    return str(datetime.strptime(time,'%Y-%m-%dT%H:%M:%S.%fZ'))

def getEventsFromAPI(url):
    headers = {
    "Accept": "application/json",
    "User-Agent": "api-doc-test-client"
    }
    response = requests.get(url, headers=headers).json()
    # Code used to print out JSON in nice format
    # print(json.dumps(response,indent=4))

    return response['events']

def convertTime(time):
    return str(datetime.strptime(time,'%Y-%m-%dT%H:%M:%S.%fZ'))

def moneyLineGames(currentEvent):

    # Only two outcomes so only two arrays needed
    homeTeam = []
    awayTeam = []
    # Append to both arrays - event name and start time
    homeTeam.append(currentEvent['name'])
    awayTeam.append(currentEvent['name'])
    homeTeam.append(convertTime(currentEvent['start']))
    awayTeam.append(convertTime(currentEvent['start']))

    event_id = currentEvent["id"]
    event_sport = getSport(currentEvent['sport-id'])

    # Get Markets - ie MoneyLine, total Goals
    for tags in currentEvent['meta-tags']:
        if(tags['type'] == "COMPETITION"):
            league = tags['name']
            # print(league)
    for market in currentEvent['markets']:
        if (market['name'] == "Moneyline"):
            # Add Moneyline to both arrays
            homeTeam.append(str(market['name']))
            awayTeam.append(str(market['name']))
            
            for index, runner in enumerate(market['runners']):
                # If index = 0 that means its the first team - Add team name to just home array
                if index == 0:                    
                    homeTeam.append(runner['name'])
                    # For home team - find the lay odds and then add to array
                    for price in runner['prices']:
                        if price['side'] == 'lay':
                            homeTeam.append(price['odds'])
                            homeTeam.append(price['available-amount'])
                            # break as soon as find lay odds, otherwise you will get other odds data
                            break
                else:
                    awayTeam.append(runner['name'])
                    # For away team - find the lay odds and then add to array
                    for price in runner['prices']:
                        if price['side'] == 'lay':
                            awayTeam.append(price['odds'])
                            awayTeam.append(price['available-amount'])
                            break
    if (len(homeTeam) == 6):
        # Changed this after so my scraped data array will have same format as this array
        row = {"Event ID": event_id,"Betting Site name": "Matchbook", "Date": homeTeam[1], "Sport": event_sport,"League" : league, "Game": homeTeam[0], "Team":homeTeam[3], "ODDS": homeTeam[4], "Liability": homeTeam[5]}
        matchbookEvents.append(row)
    if (len(awayTeam) == 6):
        row = {"Event ID": event_id,"Betting Site name": "Matchbook", "Date": awayTeam[1], "Sport": event_sport, "League" : league, "Game": awayTeam[0], "Team":awayTeam[3], "ODDS": awayTeam[4], "Liability": awayTeam[5]}
        matchbookEvents.append(row) 

def soccerGames(currentEvent):
    homeTeam = []
    awayTeam = []
    draw = []
    # Append to all three arrays - event name and start time
    homeTeam.append(currentEvent['name'])
    awayTeam.append(currentEvent['name'])
    draw.append(currentEvent['name'])
    homeTeam.append(convertTime(currentEvent['start']))
    awayTeam.append(convertTime(currentEvent['start']))
    draw.append(convertTime(currentEvent['start']))

    event_id = currentEvent["id"]
    event_sport = getSport(currentEvent['sport-id'])

    # Get Markets - ie Match odds
    for tags in currentEvent['meta-tags']:
        if(tags['type'] == "COMPETITION"):
            league = tags['name']
            # print(league)
    for market in currentEvent['markets']:
        if (market['name'] == "Match Odds"):
            homeTeam.append(market['name'])
            awayTeam.append(market['name'])
            draw.append(market['name'])
            for index, runner in enumerate(market['runners']):
                if index == 0:
                    homeTeam.append(runner['name'])
                    # For home team - find the lay odds and then add to array
                    for price in runner['prices']:
                        if price['side'] == 'lay':
                            homeTeam.append(price['odds'])
                            homeTeam.append(price['available-amount'])
                            # break as soon as find lay odds, otherwise you will get other odds data
                            break
                elif index == 1:
                    awayTeam.append(runner['name'])
                    for price in runner['prices']:
                        if price['side'] == 'lay':
                            awayTeam.append(price['odds'])
                            awayTeam.append(price['available-amount'])
                            # break as soon as find lay odds, otherwise you will get other odds data
                            break            
                else:
                    draw.append('Draw')
                    for price in runner['prices']:
                        if price['side'] == 'lay':
                            draw.append(price['odds'])
                            draw.append(price['available-amount'])
                            # break as soon as find lay odds, otherwise you will get other odds data
                            break    
    if (len(homeTeam) == 6):
        row = {"Event ID": event_id,"Betting Site name": "Matchbook", "Date": homeTeam[1], "Sport": event_sport, "League" : league,  "Game": homeTeam[0], "Team":homeTeam[3], "ODDS": homeTeam[4],"Liability": homeTeam[5]}
        matchbookEvents.append(row)
    if (len(awayTeam) == 6):
        row = {"Event ID": event_id,"Betting Site name": "Matchbook", "Date": awayTeam[1], "Sport": event_sport, "League" : league,  "Game": awayTeam[0], "Team":awayTeam[3], "ODDS": awayTeam[4],"Liability": awayTeam[5]}
        matchbookEvents.append(row)
    if (len(draw) == 6):
        row = {"Event ID": event_id,"Betting Site name": "Matchbook", "Date": draw[1], "Sport": event_sport, "League" : league, "Game": draw[0], "Team":draw[3], "ODDS": draw[4],"Liability": draw[5]}
        matchbookEvents.append(row) 

matchbookEvents = []
filtered_rows = []

def gatherData():
    matchbookEvents.clear()
    for event in getEventsFromAPI(url):
        if event['sport-id'] == 15:
            soccerGames(event)
        else:
            moneyLineGames(event)

    filtered_rows.clear()

    for i in matchbookEvents:
        if(i["League"] in ["Major League Baseball", "Spain La Liga", "Germany Bundesliga", "US Major League Soccer", "England Championship", "England Premier League", "Italy Serie A", "France Ligue 1", "UEFA Champions League", "NFL" , "NHL", "NBA"]):
            
            filtered_rows.append(i)
    
    return filtered_rows

# for i in gatherData():
#     print(i)


# for i in gatherData():
#     print(i)

# for i in range(0,4):
#     print(len(gatherData()))
#     print()