from flask import jsonify, request, current_app, url_for
from . import api
from ..helpers import LastUpdatedOrderedDict as oD
from ..helpers import UnicodeReader
from .. import db
from ..helpers import UnicodeReader, ParseUrlCsv, shell

#start importer dependencies
#import os, time, json


from ..models import Coffeestate

@api.route('/state/', methods=['GET'])
def state():
    if request.method == 'GET':
        
        return_data = {}
        data = {}
        if len(request.args) > 0:
            data = {
                'power': request.args.get('power'),
                'brew': request.args.get('brew')
            }
            
            coffeestate = Coffeestate.query.first()
                        
            if isinstance(coffeestate, Coffeestate):    
                if data['power'] == 'Off' or data['power'] == 'On':
                    coffeestate.power = data['power']
                if data['brew'] == 'Light' or data['brew'] == 'Medium' or data['brew'] == 'Strong':
                    coffeestate.brew = data['brew']
            
                #db.session.add(coffeestate)
                db.session.commit()
                return_data['success'] = 'success'
                return_data['power'] = coffeestate.power
                return_data['brew'] = coffeestate.brew
            
        else:
            coffeestate = Coffeestate.query.first()
            return_data = {}
            
            if isinstance(coffeestate, Coffeestate):                
                return_data['power'] = coffeestate.power
                return_data['brew'] = coffeestate.brew
                
        return jsonify(data=return_data)
        
       
    