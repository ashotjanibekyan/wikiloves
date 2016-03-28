#!/usr/bin/python
# -*- coding: utf-8  -*-

from flask import Flask, render_template
import json, os, time, re

app = Flask(__name__)
app.debug = True

try:
    with open('db.json', 'r') as f:
        db = json.load(f)
except:
    db = None
menu = {name: sorted(e[-4:] for e in db if e[:-4] == name) for name in set(e[:-4] for e in db)}
mainData = {name: {e[-4:]:
    {'count': sum(db[e][c]['count'] for c in db[e]), 
     'usercount': sum(db[e][c]['usercount'] for c in db[e]),
     'usage': sum(db[e][c]['usage'] for c in db[e])}
    for e in db if e[:-4] == name} for name in set(e[:-4] for e in db)}

@app.route('/')
def index():
    return render_template('mainpage.html', title=u'Wiki Loves Competitions Tools', menu=menu, data=mainData)

@app.route('/log')
def logpage():
    try:
        with open('update.log', 'r') as f:
            log = f.read()
        timestamp = time.strftime('%H:%M, %d %B %Y', time.strptime(log[:14], '%Y%m%d%H%M%S'))
        log = re.sub(ur'\[\[([^]]+)\]\]', lambda m: u'<a href="https://commons.wikimedia.org/wiki/%s">%s</a>' %
                (m.group(1).replace(u' ', u'_'), m.group(1)), log[15:]).split(u'\n')
    except:
        log = timestamp = None
    return render_template('log.html', title=u'Update log', menu=menu, time=timestamp, log=log)

@app.route('/<name>')
def event_main(name):
    if not db:
        return index()
    if name in mainData:
        eventName = u'Wiki Loves %s' % name.capitalize()
        eventData = mainData[name]
        eventData.update(contries={c: {e[-4:]:
            {'count': db[e][c]['count'], 'usercount': db[e][c]['usercount'], 'usage': db[e][c]['usage']}
            for e in db if e[:-4] == name and c in db[e]}
            for c in set(c for e in db if e[:-4] == name for c in db[e])})
        return render_template('eventmain.html', title=eventName, menu=menu, name=name, data=eventData)
    else:
        return render_template('page_not_found.html', title=u'Event not found', menu=menu)

@app.route('/<name>/<year>')
def event_year(name, year):
    if not db:
        return index()
    event = name + year
    if event in db:
        eventName = u'Wiki Loves %s %s' % (name.capitalize(), year)
        eventData = {c: {d: db[event][c][d] for d in db[event][c] if d != 'users'} for c in db[event]}
        return render_template('event.html', title=eventName, menu=menu, name=name, year=year, data=eventData)
    else:
        return render_template('page_not_found.html', title=u'Event not found', menu=menu)

@app.route('/<name>/<year>/<country>')
def users(name, year, country):
    if not db:
        return index()
    event = name + year
    if event in db and country in db[event]:
        eventName = u'Wiki Loves %s %s in %s' % (name.capitalize(), year, country)
        eventUsers = db[event][country]['users']
        return render_template('users.html', title=eventName, menu=menu, name=name, year=year,
                               country=country, data=eventUsers)
    elif event in db:
        return render_template('page_not_found.html', title=u'Country not found', menu=menu)
    else:
        return render_template('page_not_found.html', title=u'Event not found', menu=menu)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html', title=u'Page not found', menu=menu), 404

if __name__ == '__main__':
    if os.uname()[1].startswith('tools-webgrid'):
        from flup.server.fcgi_fork import WSGIServer
        WSGIServer(app).run()
    else:
        # Roda fora do Labs
        app.run()
