from decimal import Decimal

from zakat360.models import User, Cause, Donation, db
from werkzeug.security import generate_password_hash


def login(client, email, password):
    return client.post("/auth/login", data={"email": email, "password": password}, follow_redirects=True)


def test_admin_manage_causes_and_update_donation_status(client, app):
    with app.app_context():
        admin = User(email="admin@example.com", username="Admin", password_hash=generate_password_hash("admin"), is_admin=True)
        user = User(email="user2@example.com", username="User2", password_hash=generate_password_hash("user"))
        cause = Cause(name="Santé", description="Aide médicale", category="Général", is_active=True)
        donation = Donation(user=user, cause=cause, amount=Decimal("1000"), status="pending")
        db.session.add_all([admin, user, cause, donation])
        db.session.commit()

    # Login as admin
    resp = login(client, "admin@example.com", "admin")
    # Some routes redirect after successful login; accept 200 or 302
    assert resp.status_code in (200, 302)

    # Create new cause
    create = client.post(
        "/admin/causes",
        data={"name": "Orphelins", "category": "Général", "description": "Aide aux orphelins", "target_amount": "0"},
        follow_redirects=True,
    )
    assert create.status_code == 200
    assert b"Orphelins" in create.data

    # Toggle existing cause active
    toggle = client.post("/admin/causes/1/toggle", follow_redirects=True)
    assert toggle.status_code == 200

    # Update donation status
    upd = client.post("/admin/donations/1/status", data={"status": "completed"}, follow_redirects=True)
    assert upd.status_code == 200

    with app.app_context():
        d = Donation.query.get(1)
        assert d.status == "completed"