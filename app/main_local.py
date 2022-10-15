'''
This main is for the local version

You'll need a local database - basically just json dump the file
then start each button click by reading it back in

$ export FLASK_APP=main_v2
$ export FLASK_ENV=development
$ flask run

'''
from flask import Flask, render_template, request, make_response, Response
from airium import Airium
import json

app = Flask(__name__)

@app.route("/game_state", methods=['POST'])
def get_accord():
    # print('here')
    
    a = Airium()
    x = 0

    if request.method == 'POST':
        
        form = request.get_json()['form']
        print(form)

        if request.form.get('action1') == 'VALUE1':
            print('value1')
            x = 1
            pass # do something
        elif  request.form.get('action2') == 'VALUE2':
            print('value2')
            x = 2
            pass # do something else
        else:
            pass # unknown
    elif request.method == 'GET':
        print('first')
        return render_template('index.html', form=request.form)
    
    print('always')
    # with a.h3(id="id23409231", klass='main_header'):
    #         a("Hello World.{0}".format(x))
    
    with a.table(id='table_372', klass='table'):
        with a.tr(klass='header_row'):
            a.th(_t='no.')
            a.th(_t='Firstname')
            a.th(_t='Lastname')

        with a.tr():
            a.td(_t='1.')
            a.td(id='jbl', _t='Jill')
            a.td(_t='Smith')  # can use _t or text

        with a.tr():
            a.td(_t='2.')
            a.td(_t='Roland', id='rmd')
            a.td(_t='Mendel')

    # ok, turns out this is all you need
    return {'result': str(a)}


# -----------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    print('GET INDEX')
    return make_response(render_template('splaynet_local.html'))