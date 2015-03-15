from flask import jsonify, request, current_app, url_for
from . import api
#from ..models import Fontfamily, Fontversion, Fontface, Fontstyle, Language, Script, Territory, Locale, Language2Territory, Locale2Territory, Language2Script
from ..helpers import LastUpdatedOrderedDict as oD
from ..helpers import UnicodeReader
from .. import db
from ..helpers import UnicodeReader, ParseUrlCsv, shell

#start importer dependencies
#import os, time, json


#from ..models import Product, Release, Fontversion2Release
from ..models import Coffeedata

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
            return_data['success'] = 'success'
            return_data['temp'] = coffeedata.temperature
            return_data['measurement_timestamp'] = coffeedata.measurement_timestamp
            
        return jsonify(data=return_data)
        
        '''
        data = {}
        sort = ''
        deepSearchFlag = False
        
        if len(request.args) > 0:
            #data = {
            #    'scripts': json.loads(request.args.get('scripts')),
            #    'styles': json.loads(request.args.get('styles')),
            #    'languages': json.loads(request.args.get('languages')),
            #    'releases': json.loads(request.args.get('releases')),
            #    'fonts': json.loads(request.args.get('fonts')),
            #    'any': json.loads(request.args.get('any')),
            #    'sort': request.args.get('sort')
            #}
            
            data = {
                'scripts': ParseUrlCsv(request.args.get('scripts')),
                'styles': ParseUrlCsv(request.args.get('styles')),
                'languages': ParseUrlCsv(request.args.get('languages')),
                'releases': ParseUrlCsv(request.args.get('releases')),
                'fonts': ParseUrlCsv(request.args.get('fonts')),
                'any': ParseUrlCsv(request.args.get('any')),
                'sort': request.args.get('sort'),
                'sample': request.args.get('sample'),
                'page': request.args.get('page'),
                'pagesize': request.args.get('pagesize'),
                'skip': request.args.get('skip')
            }
            sort = request.args.get('sort')

            deep = request.args.get('deep')
            if deep == 'true':
                deepSearchFlag = True

            #print data['any']
        (fontfamilies, family_count, face_count, compare_from_string, compare_to_string) = Fontfamily.GetAllFonts(data, deepSearchFlag, False)
        
        return jsonify(fontfamilies=fontfamilies, family_count=family_count, face_count=face_count, sort=sort, compare_from_string=compare_from_string, compare_to_string=compare_to_string)
        '''
    
'''    
@api.route('/test/') 
def test():

    #results = db.session.query(Fontfamily, Fontface, Fontversion).join('fontfaces', 'fontversions').filter(and_(Fontfamily.is_retired==False, Fontface.is_retired==False, Fontversion.is_retired==False, Fontversion.is_latest_version==True)).filter(Fontversion.metadata_json.contains(['en'])).order_by(Fontfamily.id).all()
    #.contains(['en']))
    
    results = db.session.query(Fontfamily, Fontface, Fontversion).join('fontfaces', 'fontversions')\
    .filter(and_(Fontfamily.is_retired==False, Fontface.is_retired==False, Fontversion.is_retired==False, Fontversion.is_latest_version==True))\
    .filter(
            cast(["af"], p.ARRAY(p.TEXT)).op("@>")(
                func.array(
                    db.session.query(
                        func.json_array_elements(Fontversion.metadata_json['MTD_Typeface_Repertoire_PrimaryScriptLanguages'])
                    )
                )
            )
    )

    query_params = {}
    query_params["fvilv"] = True
    query_params["fvpl"] = 'am'
    query_params["fvpsls"] = '{"\\"am\\"", "\\"ti\\""}'

    
    results = db.session.query(Fontfamily, Fontface, Fontversion).from_statement(
                "SELECT fontversion.id as fontversion_id, fontface.id as fontface_id, fontfamily.id as fontfamily_id,\
                fontversion.version as fontversion_version, fontversion.file_location as fontversion_file_location,\
                fontversion.svn_revision_number as fontversion_svn_revision_number, fontversion.svn_path as fontversion_svn_path,\
                fontfamily.name as fontfamily_name, fontface.postscript_name as fontface_postscript_name, fontface.style_name as fontface_style_name,\
                fontface.full_name as fontface_full_name,\
                fontversion.metadata_json as fontversion_metadata_json\
                FROM fontfamily\
                JOIN fontface ON fontfamily.id = fontface.fontfamily_id\
                JOIN fontversion ON fontface.id = fontversion.fontface_id\
                WHERE fontversion.is_retired = false AND fontface.is_retired = false AND fontfamily.is_retired = false\
                AND fontversion.is_latest_version = :fvilv\
                AND fontversion.metadata_json->>'MTD_Typeface_Repertoire_PrimaryLanguage' = :fvpl\
                AND (:fvpsls) <@ array(SELECT json_array_elements(fontversion.metadata_json -> 'MTD_Typeface_Repertoire_PrimaryScriptLanguages')::text)\
                ORDER BY fontfamily.id, fontface.id, fontversion.id"
            ).params(**query_params).all()

    #.params(fvilv=True, fvpl='am', fvpsls=str('{"\\"am\\"", "\\"ti\\""}')).all()
    #('{"\"en\"", "\"uk\""}')
    #'\"am\"', '\"af\"'
    #.filter(cast(Fontversion.metadata_json['MTD_Typeface_Repertoire_PrimaryScript'], p.TEXT)=='"Latin"')\
    
    
    #db.session.query(func.array_agg(func.json_array_elements(cast(Fontversion.metadata_json['MTD_Typeface_Repertoire_PrimaryScriptLanguages'], postgresql.TEXT))))
    
    #.filter(cast(func.json_array_elements(Fontversion.metadata_json['MTD_Typeface_Repertoire_PrimaryScriptLanguages']), postgresql.TEXT).contains(postgresql.array(['"en"', '"uk"'])))
    
    #.filter(cast(func.json_array_elements(Fontversion.metadata_json['MTD_Typeface_Repertoire_PrimaryScriptLanguages']), postgresql.TEXT).contains(postgresql.array(['"en"', '"uk"'])))
    #.filter(cast(Fontversion.metadata_json['MTD_Typeface_Repertoire_PrimaryScriptLanguages'], postgresql.TEXT).contains(postgresql.array(['"en"'])))

    #
    
    
    
    json_results = []
    for (fam, face, ver) in results:
        #json_results.append(fam)
        print fam, face, ver
    return jsonify(output=json_results)     
'''