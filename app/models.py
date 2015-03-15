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

'''
class City(db.Model, AutoSerialize):
    __tablename__ = 'city'
    __public__ = ('id', 'name', 'url_name')

    id = db.Column(db.BigInteger, primary_key = True)
    name = db.Column(db.String)
    url_name = db.Column(db.String)

    def __init__(self, name, url_name):
        self.name = name
        self.url_name = url_name
        
    def __repr__(self):
        return '<City %r %r>' % (unicode(self.id), unicode(self.name))
'''       

class Coffeedata(db.Model, AutoSerialize):
    __tablename__ = 'coffeedata'
    __public__ = ('id', 'temperature')
    #we're going to use 'id' as the url_name for users, because email addresses, display names, usernames, etc. can be duplicated across domains
    #   the only unique field is actually apple_id and by extension, our generated primary key 'id'

    id = db.Column(db.BigInteger, primary_key = True)
    #city_id = db.Column(db.BigInteger, db.ForeignKey('city.id'))
    temperature = db.Column(db.Numeric)
    #humidity = db.Column(db.Numeric)
    #light = db.Column(db.Numeric)
    #airquality_raw = db.Column(db.Numeric)
    #sound = db.Column(db.Numeric)
    #dust = db.Column(db.Numeric)
    
    measurement_timestamp = db.Column(db.DateTime)
    
    #def __init__(self, city_id, temperature, humidity, light, airquality_raw, sound, dust, measurement_timestamp=None):
    def __init__(self, temperature, measurement_timestamp=None):
        #self.city_id = city_id
        self.temperature = temperature
        #self.humidity = humidity
        #self.light = light
        #self.airquality_raw = airquality_raw
        #self.sound = sound
        #self.dust = dust
        current_datetime = datetime.utcnow()
        if measurement_timestamp is None:
            measurement_timestamp = current_datetime
        self.measurement_timestamp = measurement_timestamp

    '''
    @staticmethod
    def Create(data):
        new_datacanvas = Coffeedata(data['temperature'])
        db.session.add(new_datacanvas)
        db.session.commit()
        return new_datacanvas
    @staticmethod
    def GetOrCreate(data):
        
        #print data['city_id']
        #print data['measurement_timestamp']
        
        datacanvas_result = Coffeedata.query.filter_by(id=data['id']).filter(Coffeedata.measurement_timestamp == data['measurement_timestamp']).first()
        #datacanvas_result = None
        if datacanvas_result is None:
            #print 'datacanvas_result is None'
            new_datacanvas = Coffeedata( data['temperature'], data['measurement_timestamp'])
            db.session.add(new_datacanvas)
            db.session.commit()
            return new_datacanvas
        else:
            #print 'datacanvas_result'
            #print datacanvas_result
            return datacanvas_result
    '''
    
    def __repr__(self):
        return '<Coffeedata %r %r %r>' % (unicode(self.id), unicode(self.temperature), unicode(self.measurement_timestamp))
