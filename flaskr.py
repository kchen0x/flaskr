#!/usr/bin/env python
# encoding: utf-8
"""
Flaskr is a light weight blog system.
"""

# all imports
import os
import sqlite3

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)

__app__ = Flask(__name__)

# Load default config and override config from an environment variable
__app__.config.update(dict(
    DATABASE=os.path.join(__app__.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='quentin',
    USERNAME='admin',
    PASSWORD='admin'
))
__app__.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    _rv = sqlite3.connect(__app__.config['DATABASE'])
    _rv.row_factory = sqlite3.Row
    return _rv


def init_db():
    """Initiate database."""
    with __app__.app_context():
        _db = get_db()
        with __app__.open_resource('schema.sql', mode='r') as schema:
            _db.cursor().executescript(schema.read())
        _db.commit()


def get_db():
    """Open a new database connection if there is none yet for the
    current application context."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@__app__.teardown_appcontext
def close_db():
    """Close the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@__app__.route('/')
def show_entries():
    """Get all the entries and render it with template."""
    _db = get_db()
    cur = _db.execute('SELECT title, text FROM entries ORDER BY id DESC;')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@__app__.route('/add/', methods=['POST'])
def add_entry():
    """Add new entry."""
    _db = get_db()
    _db.execute('INSERT INTO entries (title, text) VALUES (?, ?)',
                [request.form['title'], request.form['text']])
    _db.commit()
    flash('New entry has been successfully posted!')
    return redirect(url_for('show_entries'))


@__app__.route('/login', methods=['GET', 'POST'])
def login():
    """Login with username and password."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != __app__.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != __app__.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@__app__.route('/logout')
def logout():
    """Logout."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    __app__.run(debug=True)
