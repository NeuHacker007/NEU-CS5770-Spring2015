#! /usr/bin/env python
# coding=utf8

import json
from flask import \
    Flask, \
    render_template, \
    make_response


app = Flask(__name__, static_folder='assets', template_folder='tmpl')
app.secret_key = open('secret').read()


@app.route('/')
def index():
    resp = make_response(render_template('index.html', ad_url=config['ad_url']))
    resp.headers['Content-Security-Policy'] =  'default-src \'self\'; '
    resp.headers['Content-Security-Policy'] += 'script-src  \'self\' \'unsafe-inline\' http://modulator.ccs.neu.edu:17605 ;'
    resp.headers['Content-Security-Policy'] += 'style-src   \'self\' \'unsafe-inline\' http://fonts.googleapis.com ;'
    resp.headers['Content-Security-Policy'] += 'font-src    \'self\' http://fonts.gstatic.com ; '
    resp.headers['Content-Security-Policy'] += 'frame-src   \'self\' http://modulator.ccs.neu.edu:17605 ;'  
    return resp

if __name__ == '__main__':
   	global config
   	config = json.load(open('config.json'))
    	app.run(host='0.0.0.0', port=config['port'])
