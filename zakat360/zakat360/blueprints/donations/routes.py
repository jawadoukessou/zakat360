import os
from decimal import Decimal, InvalidOperation
from flask import render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import current_user

from . import donations_bp
from ...extensions import db
from ...models import Donation, Cause

@donations_bp.route('/')
def index():
    """Liste des dons (publique simplifiée)"""
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    return render_template('donations/index.html', donations=donations)

@donations_bp.route('/new', methods=['GET', 'POST'])
def new():
    """Page de création de don et traitement du formulaire"""
    if request.method == 'POST':
        cause_id = request.form.get('cause_id')
        amount = request.form.get('amount')
        donor_name = request.form.get('donor_name') or None
        payment_method = request.form.get('payment_method') or 'card'
        anonymous = bool(request.form.get('anonymous'))

        # Validation simple
        if not cause_id or not amount:
            flash('Veuillez sélectionner une cause et saisir un montant.', 'danger')
            return redirect(url_for('donations.new'))
        try:
            amount_dec = Decimal(amount)
            if amount_dec <= 0:
                raise InvalidOperation
        except Exception:
            flash('Montant invalide.', 'danger')
            return redirect(url_for('donations.new'))

        cause = Cause.query.get(int(cause_id))
        if not cause:
            flash('Cause introuvable.', 'danger')
            return redirect(url_for('donations.new'))

        # Gérer preuve (optionnelle)
        proof_file = request.files.get('proof')

        donation = Donation(
            cause_id=cause.id,
            amount=amount_dec,
            donor_name=donor_name if not anonymous else 'Anonyme',
            payment_method=payment_method,
            status='completed',
            user_id=(current_user.id if (hasattr(current_user, 'is_authenticated') and current_user.is_authenticated and not anonymous) else None)
        )
        db.session.add(donation)
        
        # Mettre à jour le montant collecté de la cause
        # Assurer une addition propre avec Decimal
        # Convertir proprement en Decimal au cas où la colonne serait Float
        base_amount = Decimal(str(cause.raised_amount)) if cause.raised_amount is not None else Decimal('0')
        cause.raised_amount = base_amount + amount_dec
        db.session.commit()

        # Sauvegarder la preuve si fournie et conforme
        if proof_file and proof_file.filename:
            allowed_ext = {'.png', '.jpg', '.jpeg', '.pdf'}
            allowed_types = {'image/png', 'image/jpeg', 'application/pdf'}
            _, ext = os.path.splitext(proof_file.filename.lower())
            if ext not in allowed_ext or proof_file.mimetype not in allowed_types:
                flash('Preuve invalide (extension ou type MIME).', 'danger')
                return redirect(url_for('donations.new'))
            # Chemin de sauvegarde
            upload_dir = current_app.config.get('UPLOAD_FOLDER')
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"donation_{donation.id}{ext}"
            file_path = os.path.join(upload_dir, filename)
            proof_file.save(file_path)
            donation.proof_path = filename
            db.session.commit()

        flash('Merci pour votre don !', 'success')
        return redirect(url_for('donations.index'))

    # GET: afficher le formulaire
    causes = Cause.query.filter_by(is_active=True).all()
    return render_template('donations/new.html', causes=causes)


@donations_bp.route('/proof/<int:donation_id>', methods=['POST'])
def upload_proof(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    proof_file = request.files.get('proof')
    if not proof_file or not proof_file.filename:
        flash('Aucun fichier fourni.', 'danger')
        return redirect(url_for('donations.index'))

    allowed_ext = {'.png', '.jpg', '.jpeg', '.pdf'}
    _, ext = os.path.splitext(proof_file.filename.lower())
    if ext not in allowed_ext:
        flash('Format de fichier non supporté. (.png, .jpg, .jpeg, .pdf)', 'danger')
        return redirect(url_for('donations.index'))

    upload_dir = current_app.config.get('UPLOAD_FOLDER')
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"donation_{donation.id}{ext}"
    file_path = os.path.join(upload_dir, filename)
    proof_file.save(file_path)
    donation.proof_path = filename
    db.session.commit()
    flash('Preuve téléchargée avec succès.', 'success')
    return redirect(url_for('donations.index'))


@donations_bp.route('/proofs/<path:filename>')
def serve_proof(filename):
    # Exposer les preuves en lecture (simple)
    upload_dir = current_app.config.get('UPLOAD_FOLDER')
    return send_from_directory(upload_dir, filename)