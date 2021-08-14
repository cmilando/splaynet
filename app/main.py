from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
import datetime

from app.process_moves import process_moves
from app.get_inprogress_game import get_move_queue

app = Flask(__name__)

# -----------------------------------------------------------------------------
def calc_move_result(form, request):

    # get queue of new moves
    move_queue, n_players = get_move_queue(form)

    # get the game_state to pretty print
    pretty_game_state = process_moves(form, move_queue, n_players)

    # get update time
    last_update = str(datetime.datetime.now())

    return [last_update, pretty_game_state]

# -----------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():

    move_result = False

    if request.method == 'POST':

        # get form data
        form = request.form

        # get move queue and new game state
        move_result = calc_move_result(form, request)

        # make response
        resp = make_response(
            render_template('splaynet.html', result=move_result))

        # save form fields
        BGA_LOGIN = form['BGA_LOGIN']
        resp.set_cookie('BGA_LOGIN', BGA_LOGIN)

        BGA_PASSWORD = form['BGA_PASSWORD']
        resp.set_cookie('BGA_PASSWORD', BGA_PASSWORD)

        BGA_NAME = form['BGA_NAME']
        resp.set_cookie('BGA_NAME', BGA_NAME)

        TABLE_ID = form['TABLE_ID']
        resp.set_cookie('TABLE_ID', TABLE_ID)

        card_1 = form['card_1']
        resp.set_cookie('card_1', card_1)

        card_2 = form['card_2']
        resp.set_cookie('card_2', card_2)

    else:
        resp = make_response(
            render_template('splaynet.html', result=move_result))

    return resp

# -----------------------------------------------------------------------------


