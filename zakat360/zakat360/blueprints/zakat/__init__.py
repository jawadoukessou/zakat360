from flask import Blueprint

zakat_bp = Blueprint('zakat', __name__, url_prefix='/zakat')

from . import routes  # noqa: F401