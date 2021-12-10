import json
import os

STATE_OPTIONS = ['hand', 'board', 'score', 'supply', 'achievement']

# Read in all cards
with open('app/json/cards_all.json') as json_file:
    CARD_DATA = json.load(json_file)

CARD_DATA_REVERSE = {o: int(key) for key,value in CARD_DATA.items() for o in value}
CARD_NAMES = [sub.replace('_', ' ') for sub in CARD_DATA_REVERSE]

states = ['hand', 'board', 'score']
state_locations = ['hand', 'board', 'score_pile']

with open('app/json/me_verbs.json') as json_file:
    me_verbs = json.load(json_file)

with open('app/json/opponent_verbs.json') as json_file:
    opponent_verbs = json.load(json_file)

span_options = ['square N age_' + str(age) for age in range(1, 11)]

compound_verbs = [
    'draw and reveal',
    'draw and tuck',
    'draw and meld',
    'draw and score',
    'draws and reveals',
    'draws and tucks',
    'draws and melds',
    'draws and scores'
]

###
Debug = False
if Debug:
    GOOGLE_CHROME_PATH = ""
    CHROMEDRIVER_PATH = "chromedriver"
else:
    GOOGLE_CHROME_PATH = os.environ.get('GOOGLE_CHROME_PATH')
    CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')