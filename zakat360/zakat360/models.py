from datetime import datetime
from flask_login import UserMixin
from .extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Champs SSO
    oauth_provider = db.Column(db.String(50), nullable=True)
    oauth_sub = db.Column(db.String(255), unique=True, nullable=True)
    is_pro = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_type = db.Column(db.String(20), default='pro')  # 'pro'
    amount = db.Column(db.Numeric(10, 2), default=20.00)  # 20 MAD/an
    currency = db.Column(db.String(10), default='MAD')
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    auto_renew = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relations
    user = db.relationship('User', lazy='joined', backref=db.backref('subscription', uselist=False))

class ScheduledDonation(db.Model):
    __tablename__ = 'scheduled_donations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cause_id = db.Column(db.Integer, db.ForeignKey('causes.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # 'weekly', 'monthly', 'yearly'
    next_execution = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relations
    user = db.relationship('User', lazy='joined', backref=db.backref('scheduled_donations', lazy='dynamic'))
    cause = db.relationship('Cause', lazy='joined')

class Cause(db.Model):
    __tablename__ = 'causes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_fr = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text)
    description_fr = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    category_fr = db.Column(db.String(50), nullable=True)
    target_amount = db.Column(db.Numeric(10, 2), default=0)
    raised_amount = db.Column(db.Numeric(10, 2), default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Donation(db.Model):
    __tablename__ = 'donations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    cause_id = db.Column(db.Integer, db.ForeignKey('causes.id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    donor_name = db.Column(db.String(100), nullable=True)
    payment_method = db.Column(db.String(50), default='card')
    status = db.Column(db.String(20), default='pending')
    proof_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relations
    user = db.relationship('User', lazy='joined', backref=db.backref('donations', lazy='dynamic'))
    cause = db.relationship('Cause', lazy='joined', backref=db.backref('donations', lazy='dynamic'))

class PriceCache(db.Model):
    __tablename__ = 'price_cache'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)  # GOLD or SILVER
    price_per_g = db.Column(db.Numeric(10, 4), nullable=False)  # en MAD par gramme
    currency = db.Column(db.String(10), default='MAD')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    route = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', lazy='joined')
