from sqlalchemy import Column, Integer, String
from app import app, db



class Link(db.Model):
    __table_name__ = 'links'
    id = db.Column(Integer, primary_key=True)
    link = db.Column(String(200), unique=True)
    title = db.Column(String(200), unique=False)
    tags = db.Column(String(200), unique=False)
    favicon = db.Column(String(200), unique=False)

    def __init__(self, link=None, title=None):
        self.link = link
        self.title = title

    def __repr__(self):
        return f'{self.link} - {self.title}'

    def json(self):
        return {'id': self.id, 'link': self.link, 'title': self.title, 'tags': self.tags}


