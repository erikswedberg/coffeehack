from datetime import datetime
from flask import current_app, request, url_for, jsonify, url_for, json
from sqlalchemy import func, distinct, desc, Sequence
from . import db
from . import pG
from .helpers import FindWhere, AutoSerialize, SanitizeURLName, UnicodeRegexpEscape, num
from .helpers import LastUpdatedOrderedDict as o
from jinja2 import Environment, PackageLoader
import re, random
import time
#from marshmallow import Serializer, fields

#env = Environment(loader=PackageLoader('app', 'templates/queries'))
   
class Coffeedata(db.Model, AutoSerialize):
    __tablename__ = 'coffeedata'
    __public__ = ('id', 'temperature')
    id = db.Column(db.BigInteger, primary_key = True)
    temperature = db.Column(db.Numeric)
    measurement_timestamp = db.Column(db.DateTime)
    
    def __init__(self, temperature, measurement_timestamp=None):
        self.temperature = temperature
        current_datetime = datetime.utcnow()
        if measurement_timestamp is None:
            measurement_timestamp = current_datetime
        self.measurement_timestamp = measurement_timestamp
    
    def __repr__(self):
        return '<Coffeedata %r %r %r>' % (unicode(self.id), unicode(self.temperature), unicode(self.measurement_timestamp))


class Coffeestate(db.Model, AutoSerialize):
    __tablename__ = 'coffeestate'
    __public__ = ('id', 'power', 'brew')
    id = db.Column(db.BigInteger, primary_key = True)
    power = db.Column(db.String)
    brew = db.Column(db.String)

    def __init__(self, power, brew=None):
        self.power = power
        self.brew = brew

    def __repr__(self):
        return '<Coffeestate %r %r %r>' % (unicode(self.id), unicode(self.power), unicode(self.brew))

