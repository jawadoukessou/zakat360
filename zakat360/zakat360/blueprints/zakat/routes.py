from decimal import Decimal
from flask import render_template, request
from flask_login import login_required

from . import zakat_bp
from ...services.price_provider import PriceProvider


@zakat_bp.route('/', methods=['GET'])
def form():
    return render_template('zakat/form.html')


@zakat_bp.route('/compute', methods=['POST'])
def compute():
    # Récupérer champs
    def to_decimal(val):
        try:
            return Decimal(str(val)) if val not in (None, '',) else Decimal('0')
        except Exception:
            return Decimal('0')

    cash_mad = to_decimal(request.form.get('cash_mad'))
    gold_g = to_decimal(request.form.get('gold_g'))
    silver_g = to_decimal(request.form.get('silver_g'))
    investments_mad = to_decimal(request.form.get('investments_mad'))
    inventory_mad = to_decimal(request.form.get('inventory_mad'))
    receivables_mad = to_decimal(request.form.get('receivables_mad'))
    dettes_ct = to_decimal(request.form.get('dettes_ct'))
    basis = (request.form.get('basis') or 'or').lower()

    # Prix
    prix_or = PriceProvider.gold_price_per_g()
    prix_argent = PriceProvider.silver_price_per_g()

    # Assiette
    assiette = cash_mad + investments_mad + inventory_mad + receivables_mad
    assiette += (gold_g * prix_or) + (silver_g * prix_argent)
    assiette -= dettes_ct
    if assiette < Decimal('0'):
        assiette = Decimal('0')

    # Nisab
    if basis == 'argent':
        nisab = Decimal('595') * prix_argent
    else:
        nisab = Decimal('85') * prix_or

    # Condition et zakat
    zakat_due = assiette * Decimal('0.025') if assiette >= nisab else Decimal('0')

    return render_template(
        'zakat/result.html',
        assiette=assiette.quantize(Decimal('0.01')),
        nisab=nisab.quantize(Decimal('0.01')),
        zakat_due=zakat_due.quantize(Decimal('0.01')),
        basis=basis,
        prix_or=prix_or,
        prix_argent=prix_argent,
    )