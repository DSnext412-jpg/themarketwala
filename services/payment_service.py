import requests
from flask import current_app


class PaymentService:

    @staticmethod
    def create_razorpay_order(amount, receipt, notes=None):
        key = current_app.config.get('RAZORPAY_KEY_ID')
        secret = current_app.config.get('RAZORPAY_SECRET')
        if not key or not secret:
            return None

        try:
            auth = (key, secret)
            data = {
                'amount': int(amount * 100),
                'currency': 'INR',
                'receipt': receipt,
                'notes': notes or {}
            }
            resp = requests.post('https://api.razorpay.com/v1/orders', json=data, auth=auth)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            return None
        return None

    @staticmethod
    def verify_payment(order_id, payment_id, signature):
        import hashlib
        import hmac

        secret = current_app.config.get('RAZORPAY_SECRET', '')
        expected = hmac.new(
            secret.encode(),
            f'{order_id}|{payment_id}'.encode(),
            hashlib.sha256
        ).hexdigest()
        return expected == signature
