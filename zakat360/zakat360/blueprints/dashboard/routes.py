from flask import render_template
from flask_login import login_required
from sqlalchemy import func

from . import dashboard_bp
from ...extensions import db
from ...models import Donation, Cause, User


@dashboard_bp.route('/')
@login_required
def index():
    # Statistiques globales
    total_donations = db.session.query(func.count(Donation.id)).scalar() or 0
    total_amount = db.session.query(func.coalesce(func.sum(Donation.amount), 0)).scalar() or 0
    total_causes = db.session.query(func.count(Cause.id)).scalar() or 0
    total_users = db.session.query(func.count(User.id)).scalar() or 0

    # Dons récents et meilleures causes
    recent_donations = Donation.query.order_by(Donation.created_at.desc()).limit(10).all()
    top_causes = Cause.query.order_by(Cause.raised_amount.desc()).limit(5).all()

    # Dons par mois (année courante)
    from datetime import datetime
    year = datetime.utcnow().year

    # Safely get the engine bind (Flask‑SQLAlchemy 3.x)
    bind = db.session.get_bind()
    dialect = bind.dialect.name if bind is not None else db.engine.dialect.name

    if dialect == 'sqlite':
        monthly = (
            db.session.query(
                func.strftime('%m', Donation.created_at).label('month'),
                func.coalesce(func.sum(Donation.amount), 0).label('total')
            )
            .filter(func.strftime('%Y', Donation.created_at) == str(year))
            .group_by('month')
            .all()
        )
    else:
        monthly = (
            db.session.query(
                func.extract('month', Donation.created_at).label('month'),
                func.coalesce(func.sum(Donation.amount), 0).label('total')
            )
            .filter(func.extract('year', Donation.created_at) == year)
            .group_by(func.extract('month', Donation.created_at))
            .all()
        )

    # Préparer 12 mois
    month_labels = [f"{i:02d}" for i in range(1, 13)]
    month_totals = []
    for i in range(1, 13):
        key = f"{i:02d}" if dialect == 'sqlite' else i
        total = next((m.total for m in monthly if m.month == key), 0)
        month_totals.append(float(total))

    return render_template(
        'dashboard/index.html',
        total_donations=total_donations,
        total_amount=total_amount,
        total_causes=total_causes,
        total_users=total_users,
        recent_donations=recent_donations,
        top_causes=top_causes,
        month_labels=month_labels,
        month_totals=month_totals,
    )