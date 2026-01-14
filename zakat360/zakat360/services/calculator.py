from decimal import Decimal, ROUND_HALF_UP
from .price_provider import PriceProvider


GOLD_NISAB_G = Decimal('85')
SILVER_NISAB_G = Decimal('595')


def compute_nisab(metal: str = 'GOLD') -> Decimal:
    metal = metal.upper()
    if metal == 'GOLD':
        price = PriceProvider.gold_price_per_g()
        return (price * GOLD_NISAB_G).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    elif metal == 'SILVER':
        price = PriceProvider.silver_price_per_g()
        return (price * SILVER_NISAB_G).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    else:
        raise ValueError('metal must be GOLD or SILVER')


def compute_due(total_assets_mad: Decimal, nisab_mad: Decimal) -> Decimal:
    if total_assets_mad < nisab_mad:
        return Decimal('0.00')
    due = (total_assets_mad * Decimal('0.025')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return due