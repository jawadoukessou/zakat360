from decimal import Decimal
from flask import request, jsonify, url_for, redirect, flash
from flask_login import current_user

from . import payments_bp
from ...extensions import db, csrf
from ...models import Donation, Cause
from ...services.paypal import PayPalClient


@payments_bp.route('/paypal/create-order', methods=['POST'])
@csrf.exempt
def paypal_create_order():
    data = request.get_json(silent=True) or {}
    amount = data.get('amount')
    cause_id = data.get('cause_id')
    if not amount or not cause_id:
        return jsonify({'error': 'missing_parameters'}), 400
    try:
        Decimal(str(amount))
    except Exception:
        return jsonify({'error': 'invalid_amount'}), 400
    if not Cause.query.get(int(cause_id)):
        return jsonify({'error': 'cause_not_found'}), 404
    client = PayPalClient()
    try:
        return_url = url_for('payments.paypal_capture_return', _external=True, cause_id=cause_id, amount=str(amount))
        cancel_url = url_for('payments.paypal_cancel_return', _external=True)
        order = client.create_order(str(amount), return_url, cancel_url)
        return jsonify(order), 200
    except Exception as e:
        return jsonify({'error': 'paypal_error', 'detail': str(e)}), 502


@payments_bp.route('/paypal/capture', methods=['POST'])
@csrf.exempt
def paypal_capture():
    data = request.get_json(silent=True) or {}
    order_id = data.get('order_id')
    cause_id = data.get('cause_id')
    donor_name = data.get('donor_name') or None
    anonymous = bool(data.get('anonymous'))
    if not order_id or not cause_id:
        return jsonify({'error': 'missing_parameters'}), 400
    cause = Cause.query.get(int(cause_id))
    if not cause:
        return jsonify({'error': 'cause_not_found'}), 404
    client = PayPalClient()
    try:
        capture = client.capture_order(order_id)
        units = capture.get('purchase_units') or []
        amount_info = (units[0].get('payments', {}).get('captures', [{}])[0].get('amount', {})) if units else {}
        value = amount_info.get('value')
        if not value:
            return jsonify({'error': 'capture_amount_missing', 'capture': capture}), 502
        amount_dec = Decimal(str(value))
        donation = Donation(
            cause_id=cause.id,
            amount=amount_dec,
            donor_name=(donor_name if not anonymous else 'Anonyme'),
            payment_method='paypal',
            status='completed',
            user_id=(current_user.id if (hasattr(current_user, 'is_authenticated') and current_user.is_authenticated and not anonymous) else None),
        )
        db.session.add(donation)
        base_amount = Decimal(str(cause.raised_amount)) if cause.raised_amount is not None else Decimal('0')
        cause.raised_amount = base_amount + amount_dec
        db.session.commit()
        return jsonify({'status': 'success', 'donation_id': donation.id, 'amount': str(amount_dec)}), 200
    except Exception as e:
        return jsonify({'error': 'paypal_error', 'detail': str(e)}), 502


@payments_bp.route('/paypal/return', methods=['GET'])
def paypal_capture_return():
    order_id = request.args.get('token')
    cause_id = request.args.get('cause_id')
    amount = request.args.get('amount')
    if not order_id or not cause_id:
        return redirect(url_for('donations.new'))
    data = {'order_id': order_id, 'cause_id': cause_id, 'donor_name': None, 'anonymous': False}
    client = PayPalClient()
    try:
        capture = client.capture_order(order_id)
        units = capture.get('purchase_units') or []
        info = (units[0].get('payments', {}).get('captures', [{}])[0].get('amount', {})) if units else {}
        value = info.get('value') or amount
        if not value:
            return redirect(url_for('donations.new'))
        cause = Cause.query.get(int(cause_id))
        if not cause:
            return redirect(url_for('donations.new'))
        dec = Decimal(str(value))
        donation = Donation(
            cause_id=cause.id,
            amount=dec,
            donor_name=None,
            payment_method='paypal',
            status='completed',
            user_id=(current_user.id if (hasattr(current_user, 'is_authenticated') and current_user.is_authenticated) else None),
        )
        db.session.add(donation)
        base = Decimal(str(cause.raised_amount)) if cause.raised_amount is not None else Decimal('0')
        cause.raised_amount = base + dec
        db.session.commit()
        flash('Merci pour votre don !', 'success')
        return redirect(url_for('donations.index'))
    except Exception:
        return redirect(url_for('donations.new'))


@payments_bp.route('/paypal/cancel', methods=['GET'])
def paypal_cancel_return():
    return jsonify({'status': 'cancelled'}), 200
