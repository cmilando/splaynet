'''
This main is for the local version

You'll need a local database - basically just json dump the file
then start each button click by reading it back in

# STEP 1 - start the `env`

then:

$ export FLASK_APP=main_local
$ export FLASK_ENV=development
$ flask run

'''
from flask import Flask, render_template, request, make_response
import jsonpickle
from class_board_v2 import Innovation, Card
from pprint import pprint

app = Flask(__name__)

# ---------------------------------------------
# this gets called by the javascript `fetch`
@app.route("/undo", methods=['POST'])
def undo_move():
    
    # read in the db
    # now the real test, read from game state
    with open('../game_data/game_state_backup.json', 'r') as infile:
        json_str = infile.read()
        game = jsonpickle.decode(json_str)
        
    # dump game_state to file
    empJson = jsonpickle.encode(game, unpicklable=True)               
    with open('../game_data/game_state.json', 'w') as outfile:
        outfile.write(empJson)                       

    # dump game state to accordion
    # this is what is caught by fetch
    # because you are doing this this way, the page doesn't re-render
    return {'result': game.pretty_dump()}

# ---------------------------------------------
# this gets called by the javascript `fetch`
@app.route("/game_state", methods=['POST'])
def get_game_state():
    
    # initialize the error message
    error_msg = False

    # get the current form object
    form = request.get_json()['form']

    if form['initialize']:
        
        print("Initialize!")

        # check starting cards
        if form['card_1'] == form['card_2']:
            error_msg = 'ERROR!: Card 1 == Card 2'
            return {'result': error_msg}

        # initialize
        n_players = int(form['n_players'])
        game = Innovation(n_players=n_players)

        # draw my first cards
        game.move_card(from_player_num=None, to_player_num="1", \
            from_state='supply', to_state='hand', card_name=form['card_1'])

        game.move_card(from_player_num=None, to_player_num="1", \
            from_state='supply', to_state='hand', card_name=form['card_2'])

        # draw everyone else's first cards
        for p in range(2, n_players + 1):
            game.move_card(from_player_num=None, to_player_num=str(p), \
                from_state='supply', to_state='hand', card_age=str(1))

            game.move_card(from_player_num=str(p), to_player_num=str(p), \
                from_state='supply', to_state='hand', card_age=str(1))  

        # dump game_state to backup file
        backup = jsonpickle.encode(game, unpicklable=True)               
        with open('../game_data/game_state_backup.json', 'w') as outfile:
            outfile.write(backup) 

    else:

        # read in the db
        # now the real test, read from game state
        with open('../game_data/game_state.json', 'r') as infile:
            json_str = infile.read()
            game = jsonpickle.decode(json_str)
        
        # dump game_state to backup file
        backup = jsonpickle.encode(game, unpicklable=True)               
        with open('../game_data/game_state_backup.json', 'w') as outfile:
            outfile.write(backup) 

        # Make move
        print("Move")
        pprint(form)
        # TODO: add a TryCatch for error_msg here
        game.move_card(from_player_num=form['from_player'],
                       to_player_num=form['to_player'],
                       from_state=form['from_state'],
                       to_state=form['to_state'],
                       card_age=form['card_age'],
                       card_name=form['card_name'])

    # dump game_state to file
    empJson = jsonpickle.encode(game, unpicklable=True)               
    with open('../game_data/game_state.json', 'w') as outfile:
        outfile.write(empJson)                       

    # dump game state to accordion
    # this is what is caught by fetch
    # because you are doing this this way, the page doesn't re-render
    if error_msg:
        return {'error_msg': error_msg}
    else:
        return {'result': game.pretty_dump()}

# -----------------------------------------------------------------------------
# this is what gets called initially
@app.route('/', methods=['GET', 'POST'])
def index():
    print('GET INDEX')
    return make_response(render_template('splaynet_local.html'))

# this should make it work but sometimes decides to fail, unclear why
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')