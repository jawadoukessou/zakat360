import os
import sys
from decimal import Decimal

# Ensure project root is on sys.path for package import
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from zakat360 import create_app, db
from zakat360.models import User, Cause, Donation, PriceCache


def main():
    app = create_app()
    with app.app_context():
        print("== Zakat360 DB Health Check ==")
        users = User.query.count()
        causes = Cause.query.count()
        donations = Donation.query.count()
        caches = PriceCache.query.count()
        print(f"Users: {users}, Causes: {causes}, Donations: {donations}, PriceCache: {caches}")

        # Sample entries
        sample_user = User.query.order_by(User.created_at.desc()).first()
        sample_cause = Cause.query.order_by(Cause.created_at.desc()).first()
        sample_donation = Donation.query.order_by(Donation.created_at.desc()).first()

        print("\n-- Samples --")
        print(f"User: {getattr(sample_user, 'email', None)} | is_admin={getattr(sample_user, 'is_admin', None)}")
        print(f"Cause: {getattr(sample_cause, 'name', None)} | cat={getattr(sample_cause, 'category', None)} | active={getattr(sample_cause, 'is_active', None)} | raised={getattr(sample_cause, 'raised_amount', None)}")
        if sample_donation:
            print(
                f"Donation: id={sample_donation.id} user_id={sample_donation.user_id} cause_id={sample_donation.cause_id} amount={sample_donation.amount} status={sample_donation.status}"
            )

        # Integrity checks
        issues = []
        # Donations with missing cause
        missing_cause = Donation.query.filter(~Donation.cause.has()).count()
        if missing_cause:
            issues.append(f"Donations without cause: {missing_cause}")
        # Donations with negative or zero amount
        neg_amount = Donation.query.filter(Donation.amount <= Decimal('0')).count()
        if neg_amount:
            issues.append(f"Donations with non-positive amount: {neg_amount}")
        # Causes with null category
        null_cat = Cause.query.filter((Cause.category.is_(None)) | (Cause.category == '')).count()
        if null_cat:
            issues.append(f"Causes with empty category: {null_cat}")
        # Users missing email or username
        bad_users = User.query.filter((User.email.is_(None)) | (User.username.is_(None))).count()
        if bad_users:
            issues.append(f"Users with missing email/username: {bad_users}")

        print("\n-- Issues --")
        if issues:
            for i in issues:
                print(f"* {i}")
        else:
            print("No structural issues detected.")

        print("\nHint: If data look wrong, you can reseed using 'python init_data.py' or delete the dev DB at 'instance/zakat360_dev.db' then run the app to recreate tables and reseed.")


if __name__ == "__main__":
    main()