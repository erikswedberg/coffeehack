from flask import render_template
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, json, g
from . import main
from .. import db
from ..models import Coffeedata
 
#from ..helpers import ParseUrlCsv
#from functools import wraps

#from urlparse import urlparse
#import urllib
#from urllib2 import urlopen, URLError
#from flask.ext.login import login_user, current_user    
#from app import login_manager


@main.route('/') 
#@login_required
def index():
    if request.method == 'GET':
                
        '''
        data = {}
        sort = ''
        sample = ''
        
        if len(request.args) > 0:
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
                'pagesize': request.args.get('pagesize')
            }
            sort = request.args.get('sort')
            sample = request.args.get('sample')
            
        if 'page' not in data or data['page'] is None:
            data['page'] = 1
            data['pagesize'] = current_app.config['FONTCATALOG_PAGE_SIZE']
                    
        #return Fontfamily.GetAllFonts(data)
        (fontfamilies, family_count, face_count, compare_from_string, compare_to_string) = Fontfamily.GetAllFonts(data, False, False)
        #(languages, language_count) = Language.GetAllLanguages(True)
        
        #print fontfamilies
        
        #print json_results
        font_json_result_obj = {}
        font_json_result_obj["fontfamilies"] = fontfamilies
        font_json_result_obj["family_count"] = family_count
        font_json_result_obj["face_count"] = face_count
        font_json_result_obj["compare_from_string"] = compare_from_string
        font_json_result_obj["compare_to_string"] = compare_to_string        
        font_json_result_obj["sort"] = sort
        font_json_result_obj["sample"] = sample

        #language_json_result_obj = {}
        #language_json_result_obj["languages"] = languages
        #language_json_result_obj["language_count"] = language_count
        
        #return json.dumps(json_result_obj)
        '''
        return render_template('index.html')
        
        #return render_template('index.html', fonts=json.dumps(font_json_result_obj))
        #return render_template('index.html', fonts=json.dumps(font_json_result_obj), languages=json.dumps(language_json_result_obj))
    #return render_template('index.html')

'''    
@main.route('/font/<path:family_url_name>')
@login_required
def family_detail(family_url_name):
    if request.method == 'GET':
        #return Fontfamily.GetAllFonts(data)
        fontfamily = Fontfamily.GetDetail(family_url_name)
        fontfamily['releases'] = Fontfamily.GetReleases(family_url_name);

        #print fontfamily        
        #print json_results
        #json_result_obj = {}
        #json_result_obj["fontfamily"] = fontfamily
        #print json.dumps(fontfamily)
        
        return render_template('family-detail.html', family=json.dumps(fontfamily))
    #return render_template('index.html')
    
@main.route('/font/<path:family_url_name>/<path:face_url_name>')
@login_required
def face_detail(family_url_name, face_url_name):
    if request.method == 'GET':
        data = {}
        #return Fontfamily.GetAllFonts(data)
        fontface = Fontface.GetDetail(face_url_name)
        

        #print fontface
        
        #print json_results
        #json_result_obj = {}
        #json_result_obj["fontfamilies"] = fontfamilies
        #json_result_obj["family_count"] = family_count
        
        #return json.dumps(json_result_obj)
        
        
        return render_template('face-detail.html', face=json.dumps(fontface))
    #return render_template('index.html')
'''