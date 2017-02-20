#!/usr/bin/env python
# encoding: utf-8
"""Flaskr is a light weight blog system.
"""

# all imports
import os
import sqlite3

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)

APP = Flask(__name__)

# Load default config and override config from an instance cfg file
APP.config.update(dict(
    DATABASE=os.path.join(APP.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='quentin',
    USERNAME='admin',
    PASSWORD='admin'
))
APP.config.from_pyfile(os.path.join(
    APP.instance_path, 'application.cfg'), silent=True)


def connect_db():
    """Connects to the specific database."""
    _rv = sqlite3.connect(APP.config['DATABASE'])
    _rv.row_factory = sqlite3.Row
    return _rv


def init_db():
    """Initiate database."""
    with APP.app_context():
        _db = get_db()
        with APP.open_resource('schema.sql', mode='r') as schema:
            _db.cursor().executescript(schema.read())
        _db.commit()


def get_db():
    """Open a new database connection if there is none yet for the
    current application context."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@APP.teardown_appcontext
def close_db(error):  # pylint: disable=locally-disabled, unused-argument
    """Close the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@APP.route('/')
def show_entries():
    """Get all the entries and render it with template."""
    _db = get_db()
    cur = _db.execute('SELECT title, text FROM entries ORDER BY id DESC;')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@APP.route('/add/', methods=['POST'])
def add_entry():
    """Add new entry."""
    _db = get_db()
    _db.execute('INSERT INTO entries (title, text) VALUES (?, ?)',
                [request.form['title'], request.form['text']])
    _db.commit()
    flash('New entry has been successfully posted!')
    return redirect(url_for('show_entries'))


@APP.route('/login', methods=['GET', 'POST'])
def login():
    """Login with username and password."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != APP.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != APP.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@APP.route('/logout')
def logout():
    """Logout."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)
