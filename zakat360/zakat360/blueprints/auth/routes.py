# (imports en haut du fichier)
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import auth_bp
from ...extensions import db, login_manager, oauth
from ...models import User
from werkzeug.security import generate_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash("Veuillez vous connecter pour accéder à cette page.", "warning")
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Identifiants invalides', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user)
        flash('Connecté avec succès', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/login.html')

@auth_bp.route('/login/google')
def login_google():
    # Vérifier que le client Google est configuré
    if not hasattr(oauth, 'google'):
        flash('SSO Google non configuré. Consultez le fichier .env pour les instructions.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Vérifier si on utilise les credentials de démo
    import os
    client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    if client_id.startswith('demo-'):
        flash('Google OAuth configuré en mode démo. Utilisez de vrais credentials Google Cloud pour l\'authentification.', 'info')
        return redirect(url_for('auth.login'))
    
    redirect_uri = url_for('auth.google_callback', _external=True)
    flash(f'URL de redirection: {redirect_uri}', 'info')
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback/google')
def google_callback():
    # 1) Afficher les erreurs renvoyées par Google directement dans l'URL
    error = request.args.get('error')
    if error:
        error_desc = request.args.get('error_description', '')
        flash(f'Échec OAuth Google: {error} {error_desc}', 'danger')
        return redirect(url_for('auth.login'))

    try:
        token = oauth.google.authorize_access_token()
        resp = oauth.google.get('userinfo')
        profile = resp.json()
    except Exception as e:
        # 2) Logger l’exception pour un diagnostic détaillé
        current_app.logger.exception("Google OAuth callback failed")
        flash(f'Échec de l’authentification Google: {e}', 'danger')
        return redirect(url_for('auth.login'))

    email = profile.get('email')
    sub = profile.get('sub')
    username = profile.get('name') or (email.split('@')[0] if email else None)
    if not email or not sub:
        flash('Profil Google incomplet (email manquant).', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter((User.oauth_provider == 'google') & (User.oauth_sub == sub)).first()
    if not user:
        # Rejoindre par email si existant
        user = User.query.filter_by(email=email).first()
        if user:
            user.oauth_provider = 'google'
            user.oauth_sub = sub
        else:
            # Créer un compte SSO avec mot de passe factice
            user = User(
                username=username or f'user_{sub[:8]}',
                email=email,
                password_hash=generate_password_hash('oauth-login'),
                oauth_provider='google',
                oauth_sub=sub,
            )
            db.session.add(user)
        db.session.commit()

    login_user(user)
    flash('Connexion via Google réussie.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà pris', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà enregistré', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Compte créé avec succès. Veuillez vous connecter.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnecté avec succès', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Gestion du changement de mot de passe
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if current_password and new_password:
            # Vérifier l'ancien mot de passe
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Mot de passe actuel incorrect.', 'danger')
                return redirect(url_for('auth.profile'))
            
            # Vérifier la correspondance des nouveaux mots de passe
            if new_password != confirm_password:
                flash('Les nouveaux mots de passe ne correspondent pas.', 'danger')
                return redirect(url_for('auth.profile'))
            
            # Mettre à jour le mot de passe
            current_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Mot de passe mis à jour avec succès.', 'success')
            return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/export')
@login_required
def export_account():
    # Export minimal RGPD-like: infos utilisateur + dons
    from ...models import Donation
    donations = Donation.query.filter_by(user_id=current_user.id).order_by(Donation.created_at.desc()).all()
    data = {
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
            'is_pro': current_user.is_pro,
        },
        'donations': [
            {
                'id': d.id,
                'cause_id': d.cause_id,
                'amount': float(d.amount),
                'status': d.status,
                'created_at': d.created_at.isoformat() if d.created_at else None,
            } for d in donations
        ]
    }
    return jsonify(data)

@auth_bp.route('/delete', methods=['POST'])
@login_required
def delete_account():
    # Supprimer le compte et anonymiser les dons
    from ...models import Donation
    try:
        Donation.query.filter_by(user_id=current_user.id).update({'user_id': None, 'donor_name': 'Anonyme'})
        u = User.query.get(current_user.id)
        logout_user()
        if u:
            from ...extensions import db
            db.session.delete(u)
            db.session.commit()
        flash('Compte supprimé et dons anonymisés.', 'info')
    except Exception:
        flash('Erreur lors de la suppression du compte.', 'danger')
    return redirect(url_for('main.index'))


@auth_bp.route('/dev/create-admin', methods=['GET'])
def dev_create_admin():
    email = 'admin@zakat360.com'
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            username='admin',
            email=email,
            password_hash=generate_password_hash('admin'),
            is_admin=True,
            is_pro=True,
        )
        db.session.add(user)
        db.session.commit()
        flash('Admin créé.', 'success')
    else:
        if not user.is_admin:
            user.is_admin = True
            db.session.commit()
        flash('Admin déjà présent.', 'info')
    return redirect(url_for('auth.login'))
