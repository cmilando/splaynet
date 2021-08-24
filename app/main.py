from flask import make_response
from flask import Flask, request, render_template, Response
from rq import Queue
from rq.job import Job
from worker import conn
import time
import json
from app.process_moves import process_moves
from app.get_inprogress_game import get_move_queue

q = Queue(connection=conn, default_timeout="10m")

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
    print('ENQUEUE')
    form = request.get_json()['form']
    job = q.enqueue(calc_move_result, form)
    return {'job_id': job.id}

@app.route('/progress/<string:job_id>')
def progress(job_id):
    def get_status():
        job = Job.fetch(job_id)
        status = job.get_status()
        print("JOB: {0}; STATUS: {1}".format(job.id, status))

        while status != 'finished':

            status = job.get_status()
            job.refresh()
            print("JOB: {0}; STATUS: {1}".format(job.id, status))

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

            time.sleep(4)

    return Response(get_status(), mimetype='text/event-stream')

# -----------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    print('GET INDEX')
    return make_response(render_template('splaynet.html'))




