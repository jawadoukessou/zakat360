import os
from flask import Flask, render_template, request, session
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from decimal import Decimal
from .extensions import db, login_manager, csrf, oauth, migrate, babel
from dotenv import load_dotenv
from sqlalchemy import func

# Charger les variables d'environnement depuis .env (du projet) en forçant l'override
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path, override=True)


def create_app():
    app = Flask(__name__)

    # Configuration minimale
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'zakat360_dev.db')
    # Ensure SQLite URI uses forward slashes on Windows
    default_db_uri = f"sqlite:///{db_path.replace('\\', '/')}"
    db_uri = os.environ.get('DATABASE_URL') or default_db_uri
    upload_dir = os.environ.get('UPLOAD_DIR') or os.path.join(basedir, 'static', 'uploads')
    is_production = os.environ.get('FLASK_ENV') == 'production'
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key'),
        'SQLALCHEMY_DATABASE_URI': db_uri,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'MAX_CONTENT_LENGTH': 8 * 1024 * 1024,  # 8 MB
        'UPLOAD_FOLDER': upload_dir,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SECURE': is_production,
        'BABEL_DEFAULT_LOCALE': 'ar',
        # Utiliser un chemin absolu pour les traductions afin d'éviter tout
        # problème de résolution en environnement Windows/IDE.
        'BABEL_TRANSLATION_DIRECTORIES': os.path.join(basedir, 'translations'),
    })

    # Fonction de sélection de locale
    def get_locale():
        # Bascule explicite via ?lang=fr|ar (priorité requête)
        lang = request.args.get('lang')
        if lang in ['fr', 'ar']:
            session['lang'] = lang
            return lang
        # Persistance: si une langue est déjà en session, la garder
        if 'lang' in session and session['lang'] in ['fr', 'ar']:
            return session['lang']
        return 'ar'

    # Initialiser les extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    oauth.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=get_locale)

    # Enregistrer le fournisseur OAuth (Google) si configuré
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    if google_client_id and google_client_secret:
    
        oauth.register(
            name='google',
            client_id=google_client_id,
            client_secret=google_client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
            token_endpoint_auth_method='client_secret_post'
        )

    # Injecter le token CSRF dans les templates
    try:
        from flask_wtf.csrf import generate_csrf

        @app.context_processor
        def inject_csrf_token():
            return dict(csrf_token=generate_csrf())
            
        @app.context_processor
        def inject_get_locale():
            return dict(get_locale=get_locale)
    except Exception:
        pass

    from .models import User  # s'assurer que les modèles sont importés

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Enregistrer les blueprints existants
    from .blueprints.donations import donations_bp
    from .blueprints.auth import auth_bp
    from .blueprints.dashboard import dashboard_bp
    from .blueprints.admin import admin_bp
    from .blueprints.zakat import zakat_bp
    from .blueprints.main import main_bp
    from .blueprints.reports import reports_bp
    from .blueprints.subscriptions import subscriptions_bp
    from .blueprints.payments import payments_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(donations_bp, url_prefix='/donations')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(zakat_bp, url_prefix='/zakat')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(subscriptions_bp, url_prefix='/subscriptions')
    app.register_blueprint(payments_bp, url_prefix='/payments')

    # Planificateur quotidien (Version Pro)
    try:
        scheduler = BackgroundScheduler(daemon=True)

        def daily_job():
            from .models import User, Donation, Cause, ScheduledDonation
            with app.app_context():
                # Traiter les dons planifiés automatiques (Version Pro)
                now = datetime.utcnow()
                scheduled_donations = ScheduledDonation.query.filter(
                    ScheduledDonation.is_active == True,
                    ScheduledDonation.next_execution <= now
                ).all()
                
                for scheduled in scheduled_donations:
                    # Créer le don automatique
                    donation = Donation(
                        cause_id=scheduled.cause_id,
                        amount=scheduled.amount,
                        donor_name=scheduled.user.username,
                        status='completed',  # Don automatique considéré comme payé
                        user_id=scheduled.user_id
                    )
                    db.session.add(donation)
                    
                    # Programmer la prochaine exécution
                    if scheduled.frequency == 'weekly':
                        scheduled.next_execution = now + timedelta(weeks=1)
                    elif scheduled.frequency == 'monthly':
                        scheduled.next_execution = now + timedelta(days=30)
                    elif scheduled.frequency == 'yearly':
                        scheduled.next_execution = now + timedelta(days=365)
                
                if scheduled_donations:
                    db.session.commit()

        scheduler.add_job(daily_job, 'cron', hour=3, minute=0)  # 03:00 UTC
        scheduler.start()
    except Exception:
        # Ne pas bloquer l'app si le scheduler échoue
        pass

    # Créer les tables si manquantes
    with app.app_context():
        db.create_all()

        # Mise à niveau légère du schéma SQLite (ajout colonne proof_path si manquante)
        try:
            from sqlalchemy import text
            engine = db.engine
            with engine.connect() as conn:
                cols = [row[1] for row in conn.execute(text("PRAGMA table_info(donations)")).fetchall()]
                if 'proof_path' not in cols:
                    conn.execute(text("ALTER TABLE donations ADD COLUMN proof_path VARCHAR(255)"))
                if 'payment_method' not in cols:
                    conn.execute(text("ALTER TABLE donations ADD COLUMN payment_method VARCHAR(50) DEFAULT 'card'"))
                # Ajouter is_admin si manquant
                user_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
                if 'is_admin' not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
        except Exception:
            # Éviter de bloquer le démarrage si l'ALTER échoue (ex: non-SQLite)
            pass

    return app
