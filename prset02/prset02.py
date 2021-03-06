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
from jinja2 import utils

app = Flask(__name__, static_folder='assets', template_folder='tmpl')
app.secret_key = open('secret').read()
user_db_path = 'user.db'
market_db_path = 'market.db'


class User(object):
    def __init__(self, name, surname, username, passwd_hash, is_admin):
        self.name = name
        self.surname = surname
        self.username = username
        self.passwd_hash = passwd_hash
        self.is_admin = is_admin
        self.is_valid = False


class Item(object):
    def __init__(self, id, author, title, desc):
        self.id = id
        self.author = author
        self.title = title
        self.desc = desc


def get_user(u):
    db = getattr(g, '_user_db', None)
    if not db:
        db = g._user_db = sqlite3.connect(user_db_path)

    cur = db.cursor()
    q = "SELECT name, surname, username, passwd, is_admin FROM users WHERE username=?;"
    cur.execute(q, (u,)) # passing value as parameters is DB safe
    rv = cur.fetchall()
    cur.close()

    if not rv:
        return None
    return User(rv[0][0], rv[0][1], rv[0][2], rv[0][3], rv[0][4])


def auth_user(u, p):
    db = getattr(g, '_user_db', None)
    if not db:
        db = g._user_db = sqlite3.connect(user_db_path)

    cur = db.cursor()
    q = "SELECT name, surname, username, passwd, is_admin FROM users WHERE username = ? ;"
    cur.execute(q, (u,)) # passing values as parameters is DB safe
    rv = cur.fetchall()
    cur.close()

    if not rv:
        return None

    u = User(rv[0][0], rv[0][1], rv[0][2], rv[0][3], rv[0][4])
    try:
        # We need DES for backwards compatibility with the mainframe.
        # But, at least we enforce a reasonable policy!  Just for
        # future reference, here's the regex: \?[A-Z]{2}[a-z]{2}[0-9]{2}!
        if des_crypt.verify(p, u.passwd_hash):
            u.is_valid = True
    except Exception, e:
        print e
    return u


def get_selling():
    db = getattr(g, '_market_db', None)
    if not db:
        db = g._market_db = sqlite3.connect(market_db_path)

    cur = db.cursor()
    q = 'SELECT id, seller, title, description FROM selling ORDER BY id DESC;'
    cur.execute(q)
    rv = cur.fetchall()
    cur.close()

    return [Item(r[0], r[1], r[2], r[3]) for r in rv]


def get_buying():
    db = getattr(g, '_market_db', None)
    if not db:
        db = g._market_db = sqlite3.connect(market_db_path)

    cur = db.cursor()
    q = 'SELECT id, buyer, title, description FROM buying ORDER BY id DESC;'
    cur.execute(q)
    rv = cur.fetchall()
    cur.close()

    return [Item(r[0], r[1], r[2], r[3]) for r in rv]


def submit_post(u, t, d, a):
    db = getattr(g, '_market_db', None)
    if not db:
        db = g._market_db = sqlite3.connect(market_db_path)

    table = 'buying'
    author_col = 'buyer'
    if a == 'sell':
        table = 'selling'
        author_col = 'seller'
    
    # XSS Protection:  HTMML-Sanitize values of title, description:
    t = utils.escape(t)
    d = utils.escape(d)

    cur = db.cursor()
    q = "INSERT INTO {0}({1}, title, description) VALUES(?, ?, ?);".format(table, author_col)
    cur.execute(q, (u.username, t, d))
    cur.close()
    db.commit()


@app.route('/')
def index():
    if 'username' not in session:
        return render_template('login.html')
    selling = get_selling()
    buying = get_buying()
    return render_template('index.html', selling=selling, buying=buying)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    u = auth_user(username, password)
    if u:
        if u.is_valid:
            session['username'] = u.username
        else:
            flash('Invalid credentials, {0}, try again'.format(u.username), 'error')
    else:
        flash('No such user {0}'.format(username), 'error')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('index'))


@app.route('/post')
def post():
    if 'username' not in session:
        return redirect(url_for('index'))

    u = get_user(session['username'])
    if not u:
        return redirect(url_for('index'))

    return render_template('post.html', user=u)


@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('index'))

    u = get_user(session['username'])
    if not u:
        return redirect(url_for('index'))

    title = request.form['title']
    desc = request.form['description']
    action = request.form['buy-or-sell']

    if not title or not desc or (action != 'buy' and action != 'sell'):
        flash('Invalid post, try again', 'error')
        return redirect(url_for('post'))

    submit_post(u, title, desc, action)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3300)
