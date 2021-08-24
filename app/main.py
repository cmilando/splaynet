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
from worker import conn
from redis import Redis

import time
import json
import os

q = Queue(connection=conn, default_timeout="10m")

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

    return pretty_game_state


@app.route('/enqueue', methods=['POST'])
def enq():
    form = request.get_json()['form']
    job = q.enqueue(calc_move_result, form)
    return {'job_id': job.id}

@app.route('/progress/<string:job_id>')
def progress(job_id):
    def get_status():
        job = Job.fetch(job_id, connection=conn)
        status = job.get_status()

        while status != 'finished':

            status = job.get_status()
            job.refresh()

            d = {'status': status}

            if 'progress' in job.meta:
                d['value'] = job.meta['progress']
            else:
                d['value'] = "Loading ..."

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
    return make_response(render_template('splaynet.html'))




