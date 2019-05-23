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
    link = request.form.get('link')

    # validity check
    # if the links lacks scheme (httml://), add it
    test = re.match(r'[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?', link)
    if not test:
        status = 400
        o = {'status': status, 'message': 'Bad request'}
        return make_response(jsonify(o), status)

    if link[:8] != 'https://':
        link = 'https://'+link

    print(link)

    try:
        rq = requests.get(url=link, timeout=10)
    except Timeout:
        status = 408
        o = {'status': status, 'message': 'Request timed out'}
        return make_response(jsonify(o), status)

    txt = rq.text
    title = None
    try:
        title = re.search('<title>(.*?)</title', txt, re.IGNORECASE).group(1)
    except AttributeError:
        title = link


    # Save link data to DB
    # If link already exists, don't save; return message

    o = {'link': link, 'title': title}

    try:
        db.session.add(model.Link(o['link'], o['title']))
        db.session.commit()
        status = 201
        o['message'] = 'Successfully Created!'

    except IntegrityError:
        status = 500
        o['message'] = 'Link creation failed'

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

