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
@app.route("/game_state", methods=['POST'])
def get_game_state():
    
    # get the current form object
    form = request.get_json()['form']
    
    # initialize
    n_players = int(form['n_players'])
    game = Innovation(n_players=n_players)

    # draw my first cards
    game.move_card(from_player_num="1", to_player_num="1", \
        from_state='supply', to_state='hand', card_name=form['card_1'])

    game.move_card(from_player_num="1", to_player_num="1", \
        from_state='supply', to_state='hand', card_name=form['card_2'])

    # dump game_state to file
    empJson = jsonpickle.encode(game, unpicklable=True)               
    with open('../game_data/game_state.json', 'w') as outfile:
        outfile.write(empJson)                       

    # now the real test, read from game state
    with open('../game_data/game_state.json', 'r') as infile:
        json_str = infile.read()
        game2 = jsonpickle.decode(json_str)

    # dump game state to accordion
    # this is what is caught by fetch
    # because you are doing this this way, the page doesn't re-render
    return {'result': game2.pretty_dump()}

# -----------------------------------------------------------------------------
# this is what gets called initially
@app.route('/', methods=['GET', 'POST'])
def index():
    print('GET INDEX')
    return make_response(render_template('splaynet_local.html'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')