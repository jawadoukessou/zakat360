from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate
from flask_babel import Babel

# Extensions (initialisées dans create_app)
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
oauth = OAuth()
migrate = Migrate()
babel = Babel()