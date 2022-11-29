from sqlalchemy.dialects.postgresql import JSON

from application.extensions import db


class Provider(db.Model):
    entity = db.Column(db.BigInteger, primary_key=True, nullable=False)
    organisation = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    entities = db.relationship("Entity", back_populates="provider")


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
    prefix = db.Column(db.Text)
    reference = db.Column(db.Text)

    organisation_entity = db.Column(db.BigInteger, db.ForeignKey("provider.entity"))
    provider = db.relationship("Provider", back_populates="entities")


class Project(db.Model):
    name = db.Column(db.Text, primary_key=True, nullable=False)
