from sqlalchemy.dialects.postgresql import JSON

from application.extensions import db


class Organisation(db.Model):

    organisation = db.Column(db.Text, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    entity = db.Column(db.Integer, nullable=False)


class Dataset(db.Model):
    dataset = db.Column(db.Text, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=True)


class Entity(db.Model):

    entity = db.Column(db.BigInteger, primary_key=True, nullable=False)
    dataset = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    entry_date = db.Column(db.Date)
    geojson = db.Column(JSON)
    json = db.Column(JSON)
    name = db.Column(db.Text)
    organisation_entity = db.Column(db.Integer, nullable=False)
    prefix = db.Column(db.Text)
    reference = db.Column(db.Text)
