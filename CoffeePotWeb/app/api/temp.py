from flask import jsonify, request, current_app, url_for
from . import api
from ..helpers import LastUpdatedOrderedDict as oD
from ..helpers import UnicodeReader
from .. import db
from ..helpers import UnicodeReader, ParseUrlCsv, shell

#start importer dependencies
#import os, time, json


from ..models import Coffeedata

@api.route('/temp', methods=['GET'])
@api.route('/temp/', methods=['GET'])
def fonts():
    if request.method == 'GET':
        
        return_data = {}
        data = {}
        if len(request.args) > 0:
            data = {
                'temperature': request.args.get('temp')
            }
            coffeedata = Coffeedata(temperature=data['temperature'])
                        
            db.session.add(coffeedata)
            db.session.commit()
            return_data['success'] = 'success'
            return_data['temp'] = str(coffeedata.temperature)
            return_data['measurement_timestamp'] = coffeedata.measurement_timestamp
            return_data['id'] = coffeedata.id
            
        else:
            coffeedatas = Coffeedata.query.all()
            return_data = []
            for cd in coffeedatas:
                
                data_temp = {}
                data_temp['id'] = cd.id
                data_temp['temp'] = str(cd.temperature)
                data_temp['measurement_timestamp'] = str(cd.measurement_timestamp)
                
                return_data.append(data_temp)
            
        return jsonify(data=return_data)
        
     