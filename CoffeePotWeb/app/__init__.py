import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
#from flask.ext.login import LoginManager
from config import config
from sqlalchemy.dialects import postgresql as pG
#from .helpers import JSONEncoder

db = SQLAlchemy()
#login_manager = LoginManager()



def create_app(config_name):
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])

    app.config.update(dict(
        JSON_SORT_KEY = False
    ))
    config[config_name].init_app(app)

    db.init_app(app)
    
    app.debug = True
    #login_manager.init_app(app)
    
    #assets.init_app(app)


    # Set the default JSON encoder
    #app.json_encoder = JSONEncoder

    '''
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        sslify = SSLify(app)
    '''
    
    '''
 
    assets = Environment(app)

    # Tell flask-assets where to look for our javascript and less files.
    assets.load_path = [
        os.path.join(os.path.dirname(__file__), 'assets/less'),
        #os.path.join(os.path.dirname(__file__), 'assets/javascript'),
        #os.path.join(os.path.dirname(__file__), 'assets/bower_components'),
    ]

    #app.debug = True;

    #{% assets "js_bundle" %}
    #    <script type="text/javascript" src="{{ ASSET_URL }}"></script>
    #{% endassets %}

    
    
    #putting all js from bower into /static/js/vendor directory, unbundled
    assets.register(
        'lesshat_indiv',
        Bundle(
            'lesshat/build/lesshat.less',
            output='../assets/less/lesshat.less'
        )
    )
    
    
    assets.register(
        'jquery_indiv',
        Bundle(
            'jquery/dist/jquery.min.js',
            output='js/lib/jquery.js'
        )
    )
    
    assets.register(
        'underscore_indiv',
        Bundle(
            'underscore/underscore.js',
            output='js/lib/underscore.js'
        )
    )
    
    assets.register(
        'require_indiv',
        Bundle(
            'requirejs/require.js',
            output='js/lib/require.js'
        )
    )
    
    assets.register(
        'requiretext_indiv',
        Bundle(
            'requirejs-text/text.js',
            output='js/lib/text.js'
        )
    )
    
    assets.register(
        'requiredomready_indiv',
        Bundle(
            'requirejs-domready/domReady.js',
            output='js/lib/domReady.js'
        )
    )
    
    assets.register(
        'nunjucks_indiv',
        Bundle(
            'nunjucks/browser/nunjucks.js',
            output='js/lib/nunjucks.js'
        )
    )
    
    assets.register(
        'history_indiv',
        Bundle(
            'history.js/scripts/bundled/html5/jquery.history.js',
            output='js/lib/history.js'
        )
    )
    
    assets.register(
        'modernizr_indiv',
        Bundle(
            'modernizr/modernizr.js',
            filters='rjsmin',
            output='js/lib/modernizr.js'
        )
    )
    
    assets.register(
        'eventemitter2_indiv',
        Bundle(
            'eventemitter2/lib/eventemitter2.js',
            filters='rjsmin',
            output='js/lib/eventemitter2.js'
        )
    )
    
    assets.register(
        'webfont_indiv',
        Bundle(
            'vendor/webfont.js',
            output='js/lib/webfont.js'
        )
    )
    
    assets.register(
        'select2_indiv',
        Bundle(
            'select2/select2.js',
            output='js/lib/select2.js'
        )
    )
    #assets.register(
    #    'select2css_indiv',
    #    Bundle(
    #        'select2/select2.css',
    #        output='../assets/less/select2.less'
    #    )
    #)
    
    assets.register(
        'bootstrap_indiv',
        Bundle(
            'bootstrap/dist/js/bootstrap.js',
            output='js/lib/bootstrap.js'
        )
    )
    
    assets.register(
        'jquery_csv_indiv',
        Bundle(
            'jquery-csv/src/jquery.csv.js',
            output='js/lib/csv.js'
        )
    )
    
    assets.register(
        'steady_indiv',
        Bundle(
            'Steady.js/Steady.js',
            output='js/lib/steady.js'
        )
    )
    
    
    #assets.register(
    #    'bootstrapless_indiv',
    #    Bundle(
    #        'bootstrap/dist/css/bootstrap.min.css',
    #        output='../assets/less/bootstrap.min.css'
    #    )
    #)
    
    
    #assets.register(
    #    'js_bundle',
    #    Bundle(
    #        'bootstrap/dist/js/bootstrap.js',
    #        'jquery-csv/src/jquery.csv.js',
    #        'requirejs-domready/domReady.js',
    #        'eventemitter2/lib/eventemitter2.js',
    #        'history.js/scripts/bundled/html5/jquery.history.js',
    #        'jquery/dist/jquery.min.js',
    #        'nunjucks/browser/nunjucks.js',
    #        'requirejs/require.js',
    #        'select2/select2.js',
    #        'requirejs-text/text.js',
    #        'underscore/underscore.js',
    #        filters='rjsmin',
    #        output='js/main2.js'
    #    )
    #)
        
    assets.register(
        'less_bundle',
        Bundle(
            'bootstrap/less/bootstrap.less',
            'bootstrap/less/theme.less',
            'select2/select2.css',
            'select2-bootstrap-css/select2-bootstrap.css',
            'fontcatalog.less',
            #filters='less,cssmin',
            filters='less',
            output='css/main.css'
        )
    )
    '''


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
