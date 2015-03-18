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
                
       
        return render_template('index.html')
        
      