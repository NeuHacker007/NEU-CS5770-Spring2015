#! /usr/bin/env python

import base64
from flask import Flask, request, render_template, make_response

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/xss/reflected')
def xss_reflected():
    msg = request.args.get('msg', 'I have nothing to say.')
    resp = make_response(render_template('xss.html', msg=msg))
    resp.headers['X-XSS-Protection'] = '0'
    return resp


@app.route('/xss/stored')
def xss_stored():
    with open('data/msg') as fd:
        msg = fd.read()
    return render_template('xss.html', msg=msg)


@app.route('/xss/input-validation')
def xss_input_validation():
    try:
        msg = request.args.get('msg', '')
        msg = base64.b64decode(msg)
    except TypeError, e:
        abort(500)
    return render_template('xss.html', msg=msg)


@app.route('/xss/output-sanitization')
def xss_output_sanitization():
    msg = request.args.get('msg', 'I have nothing to say.')
    resp = make_response(render_template('sanitize.html', msg=msg))
    resp.headers['X-XSS-Protection'] = '0'
    return resp


@app.route('/xss/csp')
def xss_csp():
    msg = request.args.get('msg', 'I have nothing to say.')
    resp = make_response(render_template('xss.html', msg=msg))
    resp.headers['X-XSS-Protection'] = '0'
    # resp.headers['Content-Security-Policy'] = 'default-src \'self\''
    # resp.headers['Content-Security-Policy'] = \
      # 'default-src \'self\' \'unsafe-inline\''
    resp.headers['Content-Security-Policy-Report-Only'] = \
        'default-src \'self\'; report-uri /reports'
    return resp


@app.route('/reports', methods=['POST'])
def reports():
    print request.data
    return 'OK'


@app.route('/cors')
def cors():
    resp = make_response(render_template('cors.html'))
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
