from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from zakat360.services.price_provider import PriceProvider
from zakat360.models import PriceCache
from zakat360.extensions import db


class DummyResp:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json


def test_cache_hit_returns_cached_prices(app):
    # Seed cache with recent entries (< 6 hours)
    now = datetime.utcnow()
    with app.app_context():
        db.session.add(PriceCache(symbol="GOLD", price_per_g=Decimal("700.00"), currency="MAD", updated_at=now))
        db.session.add(PriceCache(symbol="SILVER", price_per_g=Decimal("10.00"), currency="MAD", updated_at=now))
        db.session.commit()

        g = PriceProvider.gold_price_per_g()
        s = PriceProvider.silver_price_per_g()

        assert g == Decimal("700.00")
        assert s == Decimal("10.00")


def test_cache_expired_fetches_api_and_caches(monkeypatch, app):
    # Expire cache (> 6 hours)
    past = datetime.utcnow() - timedelta(hours=7)
    with app.app_context():
        db.session.add(PriceCache(symbol="GOLD", price_per_g=Decimal("600.00"), currency="MAD", updated_at=past))
        db.session.add(PriceCache(symbol="SILVER", price_per_g=Decimal("8.00"), currency="MAD", updated_at=past))
        db.session.commit()

    def fake_get(url, params=None, timeout=5):
        # Simulate Metals API-like response in MAD per gram
        return DummyResp({
            "rates": {
                "XAU": 700.0,  # gold per gram
                "XAG": 10.0,   # silver per gram
            }
        })

    monkeypatch.setattr("requests.get", fake_get, raising=False)

    g = PriceProvider.gold_price_per_g()
    s = PriceProvider.silver_price_per_g()

    assert g == Decimal("700.0")
    assert s == Decimal("10.0")

    # Verify new cache timestamps are recent
    with app.app_context():
        cg = PriceCache.query.filter_by(symbol="GOLD").order_by(PriceCache.updated_at.desc()).first()
        cs = PriceCache.query.filter_by(symbol="SILVER").order_by(PriceCache.updated_at.desc()).first()
        assert cg is not None and cs is not None
        assert (datetime.utcnow() - cg.updated_at).total_seconds() < 60
        assert (datetime.utcnow() - cs.updated_at).total_seconds() < 60