from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import get_locale
from sqlalchemy import func, cast, String
from datetime import datetime, timedelta

from . import admin_bp
from ...extensions import db
from ...models import Cause, Donation, AuditLog


def admin_required():
    if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
        flash('Accès admin requis.', 'danger')
        return False
    return True


def log_action(action: str, route: str, details: str = None):
    try:
        entry = AuditLog(user_id=(current_user.id if hasattr(current_user, 'id') else None), action=action, route=route, details=details)
        db.session.add(entry)
        db.session.commit()
    except Exception:
        db.session.rollback()


@admin_bp.route('/')
@login_required
def index():
    if not admin_required():
        return redirect(url_for('main.index'))
    # Total dons (nombre)
    total_donations = db.session.query(func.count(Donation.id)).scalar() or 0
    # Dons aujourd'hui (UTC)
    start_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_donations = db.session.query(func.count(Donation.id)).filter(Donation.created_at >= start_today).scalar() or 0
    # Dons ce mois (UTC)
    start_month = start_today.replace(day=1)
    month_donations = db.session.query(func.count(Donation.id)).filter(Donation.created_at >= start_month).scalar() or 0
    # Cause la plus soutenue (par nombre de dons)
    top = (
        db.session.query(Cause, func.count(Donation.id).label('cnt'))
        .join(Donation, Donation.cause_id == Cause.id)
        .group_by(Cause.id)
        .order_by(func.count(Donation.id).desc())
        .first()
    )
    top_cause_obj = top[0] if top else None
    # Donateurs uniques: user_id distinct + donor_name distinct (quand user_id NULL)
    unique_users = db.session.query(func.count(func.distinct(Donation.user_id))).filter(Donation.user_id.isnot(None)).scalar() or 0
    unique_named = db.session.query(func.count(func.distinct(Donation.donor_name))).filter(Donation.user_id.is_(None), Donation.donor_name.isnot(None)).scalar() or 0
    unique_donors = unique_users + unique_named
    stats = {
        'donations': total_donations,
        'today': today_donations,
        'month': month_donations,
        'top_cause': top_cause_obj,
        'unique_donors': unique_donors,
    }
    recent_rows = (
        db.session.query(Donation, Cause)
        .join(Cause, Donation.cause_id == Cause.id)
        .order_by(Donation.created_at.desc())
        .limit(8)
        .all()
    )
    recent = [
        {
            'cause': r[1].name,
            'cause_obj': r[1],
            'amount': float(r[0].amount),
            'donor': r[0].donor_name or ('Utilisateur' if r[0].user_id else 'Anonyme'),
            'created_at': r[0].created_at,
            'status': r[0].status,
        }
        for r in recent_rows
    ]
    cat_rows = (
        db.session.query(Cause.category, func.sum(Donation.amount), Cause.category_fr)
        .join(Donation, Donation.cause_id == Cause.id)
        .group_by(Cause.category, Cause.category_fr)
        .all()
    )
    is_fr = str(get_locale()) == 'fr'
    cat_labels = [(row[2] if is_fr and row[2] else row[0]) or '—' for row in cat_rows]
    cat_data = [float(row[1]) for row in cat_rows]
    year = datetime.utcnow().year
    start_year = datetime(year, 1, 1)
    end_year = datetime(year + 1, 1, 1)
    year_rows = (
        db.session.query(Donation)
        .filter(Donation.created_at >= start_year, Donation.created_at < end_year)
        .all()
    )
    month_data = [0.0] * 12
    for d in year_rows:
        if d.created_at:
            m = d.created_at.month
            month_data[m - 1] += float(d.amount)
    month_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    charts = {
        'categories': {'labels': cat_labels, 'data': cat_data},
        'months': {'labels': month_labels, 'data': month_data},
    }
    return render_template('admin/index.html', stats=stats, recent=recent, charts=charts)


@admin_bp.route('/causes', methods=['GET', 'POST'])
@login_required
def causes():
    if not admin_required():
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        target = request.form.get('target_amount', '0')
        try:
            from decimal import Decimal
            cause = Cause(name=name, category=category, description=description, target_amount=Decimal(target), raised_amount=0, is_active=True)
            db.session.add(cause)
            db.session.commit()
            log_action('create_cause', '/admin/causes', f"name={name}")
            flash('Cause créée.', 'success')
        except Exception:
            db.session.rollback()
            flash('Erreur lors de la création de la cause.', 'danger')
        return redirect(url_for('admin.causes'))
    causes = Cause.query.order_by(Cause.created_at.desc()).all()
    return render_template('admin/causes.html', causes=causes)


@admin_bp.route('/causes/<int:cause_id>/toggle', methods=['POST'])
@login_required
def toggle_cause(cause_id):
    if not admin_required():
        return redirect(url_for('main.index'))
    cause = Cause.query.get_or_404(cause_id)
    cause.is_active = not cause.is_active
    db.session.commit()
    log_action('toggle_cause', f'/admin/causes/{cause_id}/toggle', f"is_active={cause.is_active}")
    flash('Statut de la cause mis à jour.', 'success')
    return redirect(url_for('admin.causes'))


@admin_bp.route('/donations/<int:donation_id>/status', methods=['POST'])
@login_required
def update_donation_status(donation_id):
    if not admin_required():
        return redirect(url_for('main.index'))
    donation = Donation.query.get_or_404(donation_id)
    status = request.form.get('status')
    if status not in {'pending', 'completed'}:
        flash('Statut invalide.', 'danger')
        return redirect(url_for('admin.index'))
    donation.status = status
    db.session.commit()
    log_action('update_donation_status', f'/admin/donations/{donation_id}/status', f"status={status}")
    flash('Statut du don mis à jour.', 'success')
    return redirect(url_for('admin.index'))
