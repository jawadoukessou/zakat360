from decimal import Decimal
from zakat360.services.calculator import compute_nisab, compute_due


def test_nisab_values(monkeypatch):
    # Mock PriceProvider to have stable prices
    from zakat360.services import price_provider

    monkeypatch.setattr(price_provider.PriceProvider, 'gold_price_per_g', lambda: Decimal('700'))
    monkeypatch.setattr(price_provider.PriceProvider, 'silver_price_per_g', lambda: Decimal('8'))

    assert compute_nisab('GOLD') == Decimal('59500.00')  # 85 * 700
    assert compute_nisab('SILVER') == Decimal('4760.00')  # 595 * 8


def test_due_calculation_rounding():
    nisab = Decimal('1000.00')
    assert compute_due(Decimal('999.99'), nisab) == Decimal('0.00')
    assert compute_due(Decimal('1000.00'), nisab) == Decimal('25.00')
    assert compute_due(Decimal('1234.56'), nisab) == Decimal('30.86')