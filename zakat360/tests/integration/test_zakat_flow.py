from decimal import Decimal

from zakat360.models import User, Cause, Donation, db
from werkzeug.security import generate_password_hash


def login(client, email, password):
    return client.post("/auth/login", data={"email": email, "password": password}, follow_redirects=True)


def test_compute_and_create_donation(client, app, monkeypatch):
    # Create user and cause
    with app.app_context():
        user = User(email="user@example.com", username="User", password_hash=generate_password_hash("pass"))
        cause = Cause(name="Éducation", description="Soutien scolaire", category="Général", is_active=True)
        db.session.add_all([user, cause])
        db.session.commit()
        user_id = user.id

    # Stabilize prices
    from zakat360.services.price_provider import PriceProvider

    monkeypatch.setattr(PriceProvider, "gold_price_per_g", lambda: Decimal("700.00"))
    monkeypatch.setattr(PriceProvider, "silver_price_per_g", lambda: Decimal("10.00"))

    # Compute zakat above nisab
    resp = client.post(
        "/zakat/compute",
        data={
            "cash_mad": "200000",
            "gold_g": "0",
            "silver_g": "0",
            "investments_mad": "0",
            "inventory_mad": "0",
            "receivables_mad": "0",
            "dettes_ct": "0",
            "basis": "or",
        },
    )
    assert resp.status_code == 200
    assert b"R\xc3\xa9sultat du calcul" in resp.data  # should render result page

    # Login
    login_resp = login(client, "user@example.com", "pass")
    assert login_resp.status_code == 200

    # Create a donation using computed amount (2.5% of 200000 = 5000)
    create_resp = client.post(
        "/donations/new",
        data={
            "amount": "5000",
            "cause_id": "1",
        },
        follow_redirects=True,
    )
    assert create_resp.status_code == 200

    # Verify persisted donation
    with app.app_context():
        donations = Donation.query.filter_by(user_id=user_id).all()
        assert len(donations) == 1
        assert donations[0].amount == Decimal("5000")
        assert donations[0].cause_id == 1