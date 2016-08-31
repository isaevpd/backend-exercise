# -*- coding: utf-8 -*-

import os.path
from flask.ext.api import FlaskAPI

SRC_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(SRC_DIR, 'data')

app = FlaskAPI(__name__)

# dummy API to serve as initial example


@app.route('/')
def home():
    return {'hello': 'world'}


@app.route('/<string:name>/', methods=['GET'])
def hello(name):
    return {'hello': name}


if __name__ == '__main__':
    app.run(debug=True)
