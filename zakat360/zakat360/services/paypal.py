import os
import requests


class PayPalClient:
    def __init__(self):
        env = os.environ.get("PAYPAL_ENV", "sandbox").lower()
        self.base = "https://api-m.paypal.com" if env == "live" else "https://api-m.sandbox.paypal.com"
        self.client_id = os.environ.get("PAYPAL_CLIENT_ID")
        self.client_secret = os.environ.get("PAYPAL_CLIENT_SECRET")
        self.currency = os.environ.get("PAYPAL_CURRENCY", "EUR")

    def _token(self):
        if not (self.client_id and self.client_secret):
            raise RuntimeError("Missing PayPal credentials")
        r = requests.post(
            f"{self.base}/v1/oauth2/token",
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()["access_token"]

    def create_order(self, amount: str, return_url: str, cancel_url: str):
        token = self._token()
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {"currency_code": self.currency, "value": str(amount)}
                }
            ],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
                "shipping_preference": "NO_SHIPPING",
                "user_action": "PAY_NOW",
            },
        }
        r = requests.post(
            f"{self.base}/v2/checkout/orders",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def capture_order(self, order_id: str):
        token = self._token()
        r = requests.post(
            f"{self.base}/v2/checkout/orders/{order_id}/capture",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
