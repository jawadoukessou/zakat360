from flask import Blueprint

donations_bp = Blueprint('donations', __name__, url_prefix='/donations')

from . import routes