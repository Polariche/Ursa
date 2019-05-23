# import flask dependencies
from flask import Flask, request, jsonify, render_template, send_from_directory, make_response
import requests
from requests.exceptions import Timeout
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
    query = db.session.query(model.Link).all()
    return jsonify([x.json() for x in query])


@app.route('/save', methods=['POST'])
def save():
    status = 500
    reg_full = r'[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?'
    reg_core = r'([https]{4,5}:\/\/[-a-zA-Z0-9@:%_\+.~#?&=]{2,256}\.[a-z]{2,4}\b)\/?'
    reg_name = r'[https]{4,5}:\/\/(?:.*\.)?([-a-zA-Z0-9@:%_\+~#?&=]{1,})\.[a-z]{2,4}\b\/?'
    link = request.form.get('link')

    # validity check
    # if the links lacks scheme (httml://), add it
    test = re.match(reg_full, link)
    if not test:
        status = 400
        o = {'status': status, 'message': 'Bad request'}
        return make_response(jsonify(o), status)

    if link[:8] != 'https://' and link[:7] != 'http://':
        link = 'https://'+link

    corelink = re.match(reg_core, link).group(1)
    # Some of website doesn't even respond (or lack a title), so there has to be a default title
    title = re.match(reg_name, corelink).group(1).title()
    print(link)
    print(name)

    # Default values
    o = {'link': link, 'title': title, 'favicon': corelink+'/favicon.ico'}

    try:
        rq = requests.get(url=link, timeout=3)
        txt = rq.text

        try:
            o['title'] = re.search('<title>(.*?)</title', txt, re.IGNORECASE).group(1)
        except AttributeError:
            print("Could not find title")

        try:
            # higher quality
            favicon = re.search('<link rel="(?:shortcut)?\s?icon" .*? href="(.*?)"', txt, re.IGNORECASE).group(1)
            
            if not re.search(reg_core, favicon):
                favicon = corelink+favicon

            if favicon[-3:] == 'png' or favicon[-3:] == 'ico':
                o['favicon'] = favicon

            print(o['favicon'])
        except AttributeError:
            print("No link rel='icon' ")

    except Timeout:
        print("Timed Out")


    # Save link data to DB
    # If link already exists, don't save; return message

    try:
        row = model.Link(o['link'], o['title'], o['favicon'])
        db.session.add(row)
        db.session.commit()
        status = 201
        o = row.json()
        o['message'] = 'Successfully Created!'

    except IntegrityError:
        status = 500
        o['message'] = 'Link creation failed'

    o['status'] = status

    return make_response(jsonify(o), status)


@app.route('/remove', methods=["POST"])
def remove():
    link = request.form.get('link')
    x = model.Link.query.filter_by(link=link)

    if not x:
        return make_response(jsonify({'message': f'link {link} does not exist', 'status': 500}), 500)

    x.delete()
    db.session.commit()

    return make_response(jsonify({'message': f'link {link} removed successfully', 'status': 200}), 200)


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

