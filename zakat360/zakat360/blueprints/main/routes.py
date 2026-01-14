from flask import render_template, request, jsonify
from sqlalchemy import func

from . import main_bp
from ...models import Cause, Donation, User
from ...extensions import db
from decimal import Decimal


@main_bp.route('/')
def index():
    # Statistiques pour la page d'accueil
    total_donations = db.session.query(func.count(Donation.id)).scalar() or 0
    total_amount = db.session.query(func.sum(Donation.amount)).scalar() or 0
    supported_causes = db.session.query(func.count(Cause.id)).scalar() or 0
    donors = db.session.query(func.count(User.id)).scalar() or 0

    return render_template('index.html',
                           total_donations=total_donations,
                           total_amount=total_amount,
                           supported_causes=supported_causes,
                           donors=donors)


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/causes')
def causes():
    category = request.args.get('category')
    query = Cause.query.filter_by(is_active=True)
    if category:
        query = query.filter(Cause.category == category)
    causes = query.order_by(Cause.created_at.desc()).all()
    return render_template('donations/causes.html', causes=causes, category=category)


@main_bp.route('/payments/webhook', methods=['POST'])
def payments_webhook():
    # Stub: juste accuser réception
    return jsonify({'status': 'received'}), 200


@main_bp.route('/dev/translate-causes-ar', methods=['GET', 'POST'])
def dev_translate_causes_ar():
    mapping = {
        "Aide Alimentaire d'Urgence": ("مساعدات غذائية عاجلة", "نوفر وجبات وطرود غذائية للأسر المحتاجة.", "طوارئ"),
        "Construction de Puits": ("حفر الآبار", "ننشئ آبار ماء صالحة للشرب في القرى الريفية لتحسين الوصول إلى المياه.", "البنية التحتية"),
        "Aide aux Orphelins": ("رعاية الأيتام", "ندعم الأطفال الأيتام بتوفير التعليم والغذاء والرعاية الصحية.", "الطفولة"),
        "Soins Médicaux Gratuits": ("رعاية صحية مجانية", "تقديم رعاية صحية وأدوية مجانية لغير القادرين.", "الصحة"),
        "Éducation pour Tous": ("التعليم للجميع", "تمويل تعليم الأطفال المحرومين وبناء المدارس.", "التعليم"),
    }
    updated = 0
    for fr_name, (ar_name, ar_desc, ar_cat) in mapping.items():
        cause = Cause.query.filter(Cause.name == fr_name).first()
        if cause:
            cause.name = ar_name
            cause.description = ar_desc
            cause.category = ar_cat
            updated += 1
    if updated:
        db.session.commit()
    return jsonify({'updated': updated}), 200
