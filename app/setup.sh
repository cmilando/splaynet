#!/bin/sh
#source ../env/bin/activate
export FLASK_APP=main_local
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run