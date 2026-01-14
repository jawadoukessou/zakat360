import os
from datetime import datetime, timedelta
from decimal import Decimal
import requests

from ..extensions import db
from ..models import PriceCache


class PriceProvider:
    """Fournit les prix des métaux avec cache DB 6h et fallback local."""

    METALS_API_URL = os.environ.get('METALS_API_URL')
    METALS_API_KEY = os.environ.get('METALS_API_KEY')
    FX_RATE_MAD = Decimal(os.environ.get('FX_RATE_MAD', '10'))  # fallback: 1 USD = 10 MAD

    @staticmethod
    def _get_cached(symbol: str):
        item = PriceCache.query.filter_by(symbol=symbol).order_by(PriceCache.updated_at.desc()).first()
        if item and item.updated_at >= datetime.utcnow() - timedelta(hours=6):
            return Decimal(item.price_per_g)
        return None

    @staticmethod
    def _set_cache(symbol: str, price_per_g: Decimal):
        item = PriceCache(symbol=symbol, price_per_g=price_per_g, currency='MAD', updated_at=datetime.utcnow())
        db.session.add(item)
        db.session.commit()

    @classmethod
    def _fallback(cls, symbol: str) -> Decimal:
        # Fallback locaux approximatifs (MAD par gramme)
        if symbol == 'GOLD':
            return Decimal('700')  # exemple: 700 MAD/g
        if symbol == 'SILVER':
            return Decimal('8')    # exemple: 8 MAD/g
        return Decimal('0')

    @classmethod
    def _fetch_api(cls, symbol: str) -> Decimal | None:
        if not (cls.METALS_API_URL and cls.METALS_API_KEY):
            return None
        try:
            # Hypothèse: API renvoie prix par once (oz) en USD
            resp = requests.get(
                cls.METALS_API_URL,
                params={'symbol': symbol, 'apikey': cls.METALS_API_KEY},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            price_per_oz_usd = Decimal(str(data.get('price_per_oz_usd')))
            grams_per_oz = Decimal('31.1034768')
            price_per_g_usd = price_per_oz_usd / grams_per_oz
            price_per_g_mad = (price_per_g_usd * cls.FX_RATE_MAD).quantize(Decimal('0.0001'))
            return price_per_g_mad
        except Exception:
            return None

    @classmethod
    def gold_price_per_g(cls) -> Decimal:
        cached = cls._get_cached('GOLD')
        if cached:
            return cached
        fetched = cls._fetch_api('GOLD')
        price = fetched if fetched is not None else cls._fallback('GOLD')
        cls._set_cache('GOLD', price)
        return price

    @classmethod
    def silver_price_per_g(cls) -> Decimal:
        cached = cls._get_cached('SILVER')
        if cached:
            return cached
        fetched = cls._fetch_api('SILVER')
        price = fetched if fetched is not None else cls._fallback('SILVER')
        cls._set_cache('SILVER', price)
        return price