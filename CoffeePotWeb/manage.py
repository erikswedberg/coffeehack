#!/usr/bin/env python
import os

from app import create_app, db
from app.models import Coffeedata
#from app.manage import ImportLegacyCityDataCommand, ImportNewCityDataCommand
from flask.ext.script import Server, Manager, Shell
#from flask.ext.assets import Environment, Bundle
#from flask.ext.assets import ManageAssets
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    

#assets.init_app(app)

manager = Manager(app)
server = Server(host="0.0.0.0", port=80)
manager.add_command('runserver', server)

#manager.add_command('import_legacy_city_data', ImportLegacyCityDataCommand())
#manager.add_command('import_new_city_data', ImportNewCityDataCommand())

#manager.add_command('list_fonts', ListFontsCommand())
#manager.add_command('assets', ManageAssets())


if __name__ == '__main__':
    manager.run()