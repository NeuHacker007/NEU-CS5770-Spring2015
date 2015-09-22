#! /usr/bin/env python

from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    data = {
        'msg': 'This is some cross-origin data.',
    }

    resp = jsonify(data)
    resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:5000'
    # resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:5001'
    # resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
