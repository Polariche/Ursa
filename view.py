# import flask dependencies
from flask import Flask, request, jsonify, render_template, send_from_directory, make_response
import requests
from requests.exceptions import Timeout, ConnectionError
import json
import random
import asyncio
import os
import re
from sqlalchemy.exc import IntegrityError

from app import app, db
import model


# default route
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/fetch', methods=['POST'])
def fetch():
    title = request.form.get('title')
    query = db.session.query(model.Link)

    if title != None:
        query = query.filter((model.Link.title.contains(title))|(model.Link.link.contains(title)))

    return jsonify([x.json() for x in query])


@app.route('/save', methods=['POST'])
def save():
    status = 500
    link = request.form.get('link')
    reg_core=r'(?:[https]{4,5}:\/\/)?([-a-zA-Z0-9\.]{2,256}\.[a-z\.]{2,5}\b)([-a-zA-Z0-9@:%_\+.~#?&//=]*)?'

    # validity check
    test = re.match(reg_core, link)

    if not test:
        status = 400
        o = {'status': status, 'message': 'Bad request'}
        return make_response(jsonify(o), status)


    tags = re.match(r'(#[a-zA-Z가-힣0-9])+', link[test.end():])
    #if tags:
    #    tags = [for i in ]

    corelink = test.group(1)
    link = f"https://{corelink}{test.group(2)}"

    # Some of website doesn't even respond (or lack a title), so there has to be a default title
    title_match = re.match(r'(?:[-a-zA-Z0-9]{2,256}\.)?([-a-zA-Z0-9]{2,256})(\.[a-z\.]{2,5})', corelink)
    title = title_match.group(1).title()
    if (len(title)<=2 or title_match.group(2) == '.io'):
        title = title + title_match.group(2)

    # Default values
    o = {'link': link, 'title': title, 'favicon': 'https://'+corelink+'/favicon.ico', 'message': ''}

    try:
        print(link)
        rq = requests.get(url=link, timeout=3)
        txt = rq.text

        try:
            o['title'] = re.search('<title>(.*?)</title>', txt, re.IGNORECASE).group(1)
        except AttributeError:
            print("Could not find title; ")

        try:
            # higher quality
            favicon = re.search(r'<link rel="(?:shortcut )?icon"[^>]*?href="(?:[https:]*\/\/)?([A-Za-z\/0-9-\.\/]*?(\.png|\.ico))(?:\?[=A-Za-z\/0-9-&]*)?"', txt, re.IGNORECASE).group(1)
            
            if not re.match(reg_core, favicon):
                favicon = corelink+favicon

            o['favicon'] = 'https://'+favicon
        except AttributeError:
            print("No link rel='icon' ")

    except Timeout:
        msg = "Warning: Timed Out"
        o['message'] = msg
        print(msg)

    except ConnectionError:
        msg = "Warning: Couldn't connect"
        o['message'] = msg
        print(msg)


    # Save link data to DB
    # If link already exists, don't save; return message

    try:
        row = model.Link(o['link'], o['title'], o['favicon'])
        db.session.add(row)
        db.session.commit()
        status = 201
        o = row.json()

    except IntegrityError:
        status = 500
        o['message'] = 'Failed to create link; Link already exists'

    o['status'] = status

    return make_response(jsonify(o), status)


@app.route('/remove', methods=["POST"])
def remove():
    id_ = request.form.get('id')
    x = model.Link.query.filter_by(id=id_)

    if not x:
        return make_response(jsonify({'message': f'id {id_} does not exist', 'status': 500}), 500)

    x.delete()
    db.session.commit()

    return make_response(jsonify({'message': f'id {id_} removed successfully', 'status': 200}), 200)


@app.route('/edit_title', methods=["POST"])
def edit_title():
    link = request.form.get('link')
    newtitle = request.form.get('newtitle')
    x = model.Link.query.filter_by(link=link)

    if not x:
        return make_response(jsonify({'message': f'link {link} does not exist', 'status': 500}), 500)

    #x.delete()
    x.title = newtitle
    db.session.commit()

    return make_response(jsonify({'message': f'link {link} modified successfully', 'status': 200}), 200)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


"""
# keeping this snippet b/c it might be useful

@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/form')
def form():
    return render_template("form.html")
    

@app.route('/submit', methods=['POST'])
def submit():
    #return f"{request.args['firstname']}, {request.args['lastname']}"
    return f"{request.form.get('firstname')}, {request.form.get('lastname')}"
"""

