from flask import Blueprint
routes = Blueprint('routes', __name__)

from web.routes.master_api import *