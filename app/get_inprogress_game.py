from selenium import webdriver
import parse
from app.config import me_verbs, opponent_verbs, \
    CARD_NAMES, span_options, compound_verbs, GOOGLE_CHROME_PATH, CHROMEDRIVER_PATH
import time
from bs4 import BeautifulSoup
from copy import deepcopy

# /////////////////////////////////////////////////////////////////////////////
def bs_parse(l):
    return BeautifulSoup(l.get_attribute('innerHTML'), 'html.parser').text

# /////////////////////////////////////////////////////////////////////////////
def get_move_queue(form):

    driver = get_webdriver(form)

    log_div = driver.find_element_by_id("logs")
    logs = log_div.find_elements_by_class_name('log')

    players = driver.find_elements_by_class_name('player-name')
    n_players = len(players)

    ## make the list of actions for given player and opponents
    me_actions = ['You ' + opt for opt in me_verbs]

    opponent_actions = [p.text + ' ' + opt for opt in opponent_verbs
                        for p in players if p.text != form['BGA_NAME']]

    moves = [None] * len(logs)

    i = 0

    # this parses new logs
    for l in logs:

        txt = bs_parse(l)
        is_me_action = any(txt.startswith(a) for a in me_actions)
        is_opponent_action = any(txt.startswith(a) for a in opponent_actions)

        # this just gets you in the door
        if is_me_action or is_opponent_action:

            # Do some cleaning
            # comment out during demo
            txt = log_clean(l)

            # get the parsed kwargs
            parsed_kwargs = get_parsed_kwargs(txt, form, players)

            moves[i] = parsed_kwargs
            i += 1


    ## trim output and reverse
    moves = moves[:i]
    moves.reverse()

    return moves, n_players

# /////////////////////////////////////////////////////////////////////////////
def log_clean(l):

    txt = bs_parse(l)

    # STEP 1) Do some basic cleaning
    # make it so this is easier to find
    if txt.find('score pile') > 0:
        txt = txt.replace('score pile', 'score_pile')

    # make card names a single string
    for card in CARD_NAMES:
        if txt.find(card) > 0:
            txt = txt.replace(card, card.replace(' ', '_'))

    # replace all compound verbs
    for cv in compound_verbs:
        if txt.find(cv) > 0:
            txt = txt.replace(cv, cv.replace(' ', '_'))

    # only save the first sentence, but keep the period!
    txt = txt.split('.')[0] + "."

    # STEP 2)
    ## This gets card age for spans, so insert this in before parsing
    ## this is only for other players so lets not worry about that yet
    is_check_html = False

    html = l.get_attribute('innerHTML')
    out_age = None
    for age in range(1, 11):
        test = html.find(span_options[age - 1])
        if test != -1:
            is_check_html = True
            out_age = age
            break

    if is_check_html:
        assert out_age
        txt = txt.replace(' a ', ' a {0} '.format(out_age))

    return txt

# /////////////////////////////////////////////////////////////////////////////
def get_webdriver(form, t_sleep=5):
    # uses spyder to get BGA logs
    # stops at the log hea

    LOGIN_URL = 'https://en.boardgamearena.com/account?'

    BGA_LOGIN = form['BGA_LOGIN']
    BGA_PASSWORD = form['BGA_PASSWORD']
    TABLE_ID = form['TABLE_ID']

    ## Set up headless webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    # set this up in Heroku dashboard
    chrome_options.binary_location = GOOGLE_CHROME_PATH

    print('Login')
    driver = webdriver.Chrome(options=chrome_options,
                              executable_path=CHROMEDRIVER_PATH)
    driver.get(LOGIN_URL)

    ## Log in using credentials
    driver.find_element_by_id('username_input').send_keys(BGA_LOGIN)
    driver.find_element_by_id('password_input').send_keys(BGA_PASSWORD)
    driver.find_element_by_id("login_button").click()

    # confirm that you actually logged in?
    time.sleep(t_sleep)

    ## Go to in-progress table
    print('Go to table table ' + TABLE_ID)
    url_game = "https://boardgamearena.com/9/innovation?table=" + TABLE_ID
    driver.get(url_game)

    return driver

# /////////////////////////////////////////////////////////////////////////////
def get_parsed_kwargs(txt, form, players):

    me_actions = ['You ' + opt for opt in me_verbs]
    is_me_action = any(txt.startswith(a) for a in me_actions)
    player_dict = {players[i - 1].text :i for i in range(1, len(players) + 1)}

    # if its a me_action
    if is_me_action:

        ## first get the verb that is being used
        ## and parse the text
        for verb in me_verbs:
            fmt_str = me_verbs[verb]['fmt_str']
            try:
                parsed_txt = parse.parse(fmt_str, txt)
                if parsed_txt:
                    break
            except:
                pass

        ##
        fmt_str = me_verbs[verb]['fmt_str']
        fmt_map = deepcopy(me_verbs[verb]['fmt_map'])

    # if its an opponent action
    else:
        for verb in opponent_verbs:
            fmt_str = opponent_verbs[verb]['fmt_str']
            try:
                parsed_txt = parse.parse(fmt_str, txt)
                if parsed_txt:
                    ## check for the edge case of return1
                    if verb == 'returns1':
                        if parsed_txt[1] in CARD_NAMES:
                            break
                    else:
                        break
            except:
                pass

        ##
        fmt_str = opponent_verbs[verb]['fmt_str']
        fmt_map = deepcopy(opponent_verbs[verb]['fmt_map'])

    ## -----------------------------------------------
    # outside the loop
    # "fmt_str": "{0} meld {1} from your hand.",
    # "subject": "0",
    # "from_player": "0",   ==> from_player_num
    # "to_player": "0",     ==> to_player_num
    # "from_state": "hand", ==> from_state
    # "to_state": "board",  ==> to_state
    # "card_age": "None",
    # "card_name": "1"

    parsed_txt = parse.parse(fmt_str, txt)

    ## so first is to fill in action with fmt_str
    ## just fill in the things with numbers
    ## this is just for {#} objects
    for obj in fmt_map:
        if fmt_map[obj].isnumeric():
            fmt_map[obj] = parsed_txt[int(fmt_map[obj])]

    ## so first is player_num lookup
    for p in ['subject', 'from_player', 'to_player']:

        if fmt_map[p] == 'None':
            continue

        for player in player_dict:
            if fmt_map[p] in [player, "{0}'s".format(player)]:
                fmt_map[p] = player_dict[player]

        if fmt_map[p] == 'their':
            fmt_map[p] = fmt_map['subject']

        if fmt_map[p] in ['You', 'you', 'your']:
            fmt_map[p] = player_dict[form['BGA_NAME']]

    ## next is state, which I think is just score_pile
    for p in ['from_state', 'to_state']:

        if fmt_map[p] == 'None':
            continue

        if fmt_map[p] in ['score_pile']:
            fmt_map[p] = 'score'

    ## finally, card age
    ## next is state, which I think is just score_pile
    for p in ['card_age']:

        if fmt_map[p] == 'None':
            continue
        else:
            fmt_map[p] = int(fmt_map[p].strip())

    ## seems like card name might need trimming? weird
    for p in ['card_name']:

        fmt_map[p] = fmt_map[p].strip()

    ## GO TIME
    kwargs = {
        'move_string': txt,
        'from_player_num': fmt_map['from_player'],
        'to_player_num': fmt_map['to_player'],
        'from_state': fmt_map['from_state'],
        'to_state': fmt_map['to_state'],
        'card_age': fmt_map['card_age'],
        'card_name': fmt_map['card_name']
    }

    return kwargs



