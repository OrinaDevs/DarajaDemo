import base64
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from django.conf import settings

def get_access_token():
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
    )
    response.raise_for_status()
    return response.json()["access_token"]

def generate_password_and_timestamp():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw_password = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(raw_password.encode()).decode()
    return password, timestamp

def format_phone_number(phone):
    """Converts 0XXXXXXXXX or +254XXXXXXXXX to 254XXXXXXXXX"""
    phone = phone.strip().replace(" ", "")
    if phone.startswith("+"):
        phone = phone[1:]
    if phone.startswith("0"):
        phone = "254" + phone[1:]

    return phone

def stk_push(phone_number, amount, account_reference="Oran Softwares", description="Payment"):
    access_token = get_access_token()
    password, timestamp = generate_password_and_timestamp()
    phone_number = format_phone_number(phone_number)

    url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    headers  = {"Authorization": f"Bearer {access_token}"}

    payload ={
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": description,
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()