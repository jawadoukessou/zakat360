from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from . import subscriptions_bp
from ...models import db, Subscription, ScheduledDonation, Cause
from ...extensions import db

@subscriptions_bp.route('/')
@login_required
def index():
    """Page principale des abonnements Pro"""
    user_subscription = current_user.subscription
    scheduled_donations = current_user.scheduled_donations.filter_by(is_active=True).all()
    
    return render_template('subscriptions/index.html', 
                         subscription=user_subscription,
                         scheduled_donations=scheduled_donations)

@subscriptions_bp.route('/upgrade', methods=['GET', 'POST'])
@login_required
def upgrade():
    """Souscrire à la version Pro"""
    if request.method == 'POST':
        # Vérifier si l'utilisateur a déjà un abonnement actif
        existing_sub = current_user.subscription
        if existing_sub and existing_sub.status == 'active' and existing_sub.end_date > datetime.utcnow():
            flash('Vous avez déjà un abonnement Pro actif.', 'info')
            return redirect(url_for('subscriptions.index'))
        
        # Créer nouvel abonnement
        end_date = datetime.utcnow() + timedelta(days=365)  # 1 an
        subscription = Subscription(
            user_id=current_user.id,
            end_date=end_date,
            amount=20.00,
            currency='MAD'
        )
        
        # Mettre à jour le statut Pro de l'utilisateur
        current_user.is_pro = True
        
        db.session.add(subscription)
        db.session.commit()
        
        flash('Félicitations ! Vous êtes maintenant membre Pro de Zakat360.', 'success')
        return redirect(url_for('subscriptions.index'))
    
    return render_template('subscriptions/upgrade.html')

@subscriptions_bp.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule_donation():
    """Planifier un don automatique (réservé aux utilisateurs Pro)"""
    if not current_user.is_pro:
        flash('Cette fonctionnalité est réservée aux membres Pro.', 'warning')
        return redirect(url_for('subscriptions.upgrade'))
    
    causes = Cause.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        cause_id = request.form.get('cause_id')
        amount = float(request.form.get('amount'))
        frequency = request.form.get('frequency')
        
        # Calculer la prochaine exécution
        next_execution = datetime.utcnow()
        if frequency == 'weekly':
            next_execution += timedelta(weeks=1)
        elif frequency == 'monthly':
            next_execution += timedelta(days=30)
        elif frequency == 'yearly':
            next_execution += timedelta(days=365)
        
        scheduled_donation = ScheduledDonation(
            user_id=current_user.id,
            cause_id=cause_id,
            amount=amount,
            frequency=frequency,
            next_execution=next_execution
        )
        
        db.session.add(scheduled_donation)
        db.session.commit()
        
        flash(f'Don automatique de {amount} MAD programmé avec succès !', 'success')
        return redirect(url_for('subscriptions.index'))
    
    return render_template('subscriptions/schedule.html', causes=causes)

@subscriptions_bp.route('/cancel/<int:schedule_id>', methods=['POST'])
@login_required
def cancel_scheduled_donation(schedule_id):
    """Annuler un don planifié"""
    scheduled_donation = ScheduledDonation.query.filter_by(
        id=schedule_id, 
        user_id=current_user.id
    ).first_or_404()
    
    scheduled_donation.is_active = False
    db.session.commit()
    
    flash('Don automatique annulé avec succès.', 'success')
    return redirect(url_for('subscriptions.index'))

@subscriptions_bp.route('/api/stats')
@login_required
def api_stats():
    """API pour les statistiques Pro"""
    if not current_user.is_pro:
        return jsonify({'error': 'Accès réservé aux membres Pro'}), 403
    
    # Statistiques des dons planifiés
    scheduled_count = current_user.scheduled_donations.filter_by(is_active=True).count()
    total_scheduled_amount = sum(
        sd.amount for sd in current_user.scheduled_donations.filter_by(is_active=True)
    )
    
    return jsonify({
        'scheduled_donations': scheduled_count,
        'total_scheduled_amount': float(total_scheduled_amount),
        'subscription_status': 'active' if current_user.subscription else 'none'
    })