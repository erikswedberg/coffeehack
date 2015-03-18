# -*- coding: utf-8 -*-
"""
    fontcatalog.manage.cldr
    ~~~~~~~~~~~~~~~~~~~~~

    cldr management commands
"""

from flask import current_app, jsonify
from flask.ext.script import Command, prompt, prompt_pass
import os, subprocess, json, tempfile, time, zipfile, shutil
from ..helpers import UnicodeReader, json_minify, SanitizeURLName

#from ..models import City, Citydata
from .. import db
