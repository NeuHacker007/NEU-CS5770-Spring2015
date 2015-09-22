#! /usr/bin/env python
# coding=utf8

import sqlite3
import markdown2
from passlib.hash import des_crypt
from flask import \
    Flask, \
    render_template, \
    json, \
    redirect, \
    abort, \
    url_for, \
    request, \
    session, \
    flash, \
    g




import pprint

class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, env, resp):
        errorlog = env['wsgi.errors']
        pprint.pprint(('REQUEST', env), stream=errorlog)

        def log_response(status, headers, *args):
            pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, *args)

        return self._app(env, log_response)

app = Flask(__name__, static_folder='assets', template_folder='tmpl')
app.secret_key = "skaodsodkosadk9idw0-2"



@app.before_request
def log_request():
    if app.config.get('LOG_REQUESTS'):
        app.logger.debug('whatever')
	print request.headers
        open(current_app.config['REQUEST_LOG_FILE'], 'w').write('...')
@app.route('/')
def index():
    return render_template('index2.html')






if __name__ == '__main__':
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    app.run(debug=True, host='0.0.0.0', port=5000)

