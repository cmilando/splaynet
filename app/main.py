from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
import datetime
from flask import Flask, redirect, url_for, request, render_template, Response
from time import sleep

from rq import Queue
from rq.job import Job
from rq import get_current_job

from redis import Redis

import time
import json
import os

r = Redis(os.environ.get('REDIS_URL', 'localhost'))
q = Queue(connection=r, default_timeout="10m")

from app.process_moves import process_moves
from app.get_inprogress_game import get_move_queue

app = Flask(__name__)

# -----------------------------------------------------------------------------
def calc_move_result(form):
    print('CALC MOVE')
    # get queue of new moves
    move_queue, n_players = get_move_queue(form)

    # get the game_state to pretty print
    pretty_game_state = process_moves(form, move_queue, n_players)

    return str(pretty_game_state)


@app.route('/enqueue', methods=['POST'])
def enq():
    print('EnQUEUE')
    form = request.get_json()['form']
    print(form)
    job = q.enqueue(calc_move_result, form)
    return {'job_id': job.id}

@app.route('/progress/<string:job_id>')
def progress(job_id):
    def get_status():
        print('GEt STATUS')
        job = Job.fetch(job_id, connection=r)
        status = job.get_status()

        while status != 'finished':

            status = job.get_status()
            job.refresh()

            d = {'status': status}

            if 'progress' in job.meta:
                d['value'] = job.meta['progress']
            else:
                d['value'] = 0

            # IF there's a result, add this to the stream
            if job.result:
                d['result'] = job.result

            json_data = json.dumps(d)
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(get_status(), mimetype='text/event-stream')

# -----------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():

    # make response
    resp = make_response(
        render_template('splaynet.html'))

    if request.method == 'POST':
        print('request = POST')
        form = request.get_json()['form']

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

    return resp

# -----------------------------------------------------------------------------


