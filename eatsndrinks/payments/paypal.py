# payments/paypal.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com"  # production: https://api-m.paypal.com

def get_access_token():
    response = requests.post(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        data={"grant_type": "client_credentials"},
    )
    return response.json()["access_token"]

def create_paypal_order(total_price_vnd):
    access_token = get_access_token()
    usd_amount = round(total_price_vnd / 25000  , 2)

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": str(usd_amount),
                }
            }
        ],
        "application_context": {
            "return_url": "https://your-frontend.com/paypal-success",
            "cancel_url": "https://your-frontend.com/paypal-cancel",
        },
    }

    response = requests.post(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    )
    return response.json()

def capture_paypal_order(paypal_order_id):
    access_token = get_access_token()
    response = requests.post(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders/{paypal_order_id}/capture",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    )
    return response.json()
