import base64
import json
import requests
from datetime import datetime
from OpenSSL import crypto

class Mpesa:
    def __init__(self):
        self.msg = ''
        self.security_credential = None
        self.consumer_key = None
        self.consumer_secret = None
        self.transaction_type = None
        self.shortcode = None
        self.store_number = None
        self.pass_key = None
        self.initiator_name = None
        self.initiator_password = None
        self.callback_url = None
        self.confirmation_url = None
        self.validation_url = None
        self.b2c_shortcode = None
        self.b2b_shortcode = None
        self.result_url = None
        self.timeout_url = None
        self.official_contact = None
        self.logo_link = None
        self.live_endpoint = 'https://api.safaricom.co.ke/'
        self.sandbox_endpoint = 'https://sandbox.safaricom.co.ke/'
        self.env = None

    def config(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise ValueError(f'Invalid config key: {key}')

    def oauth_token(self):
        url = self.env_url('oauth/v1/generate?grant_type=client_credentials')
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()}'
        }
        response = requests.get(url, headers=headers, verify=True)
        response.raise_for_status()
        return response.json().get('access_token')

    def register_url(self, status='Cancelled', version='v1'):
        url = self.env_url(f'mpesa/c2b/{version}/registerurl')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.oauth_token()}'
        }
        payload = {
            'ShortCode': self.shortcode,
            'ResponseType': status,
            'ConfirmationURL': self.confirmation_url,
            'ValidationURL': self.validation_url
        }
        self.http_post(url, headers, payload)

    def STKPush(self, amount, phone_number_sending_fund, account_reference, transaction_desc):
        url = self.env_url('mpesa/stkpush/v1/processrequest')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.oauth_token()}'
        }
        payload = {
            'BusinessShortCode': self.shortcode if self.transaction_type.lower() == 'paybill' else self.store_number,
            'Password': self.password(),
            'Timestamp': self.timestamp(),
            'TransactionType': self.transaction_type_conversion(),
            'Amount': amount,
            'PhoneNumber': phone_number_sending_fund,
            'PartyA': phone_number_sending_fund,
            'PartyB': self.shortcode,
            'CallBackURL': self.callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        return self.http_post(url, headers, payload)

    def transaction_type_conversion(self):
        return 'CustomerPayBillOnline' if self.transaction_type.lower() == 'paybill' else 'CustomerBuyGoodsOnline'

    def STKPushQuery(self, checkout_request_id):
        url = self.env_url('mpesa/stkpushquery/v1/query')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.oauth_token()}'
        }
        payload = {
            'BusinessShortCode': self.shortcode if self.transaction_type.lower() == 'paybill' else self.store_number,
            'Password': self.password(),
            'Timestamp': self.timestamp(),
            'CheckoutRequestID': checkout_request_id
        }
        self.http_post(url, headers, payload)

    def reversal(self, amount, transaction_id, remarks, result_url='reversal', timeout_url='reversal', occasion=None):
        url = self.env_url('mpesa/reversal/v1/request')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.oauth_token()}'
        }
        payload = {
            'Initiator': self.initiator_name,
            'SecurityCredential': self.security_credential_encryption(),
            'CommandID': 'TransactionReversal',
            'TransactionID': transaction_id,
            'Amount': amount,
            'ReceiverParty': self.shortcode if self.transaction_type.lower() == 'paybill' else self.store_number,
            'RecieverIdentifierType': 11,
            'ResultURL': f'{self.result_url}/{result_url}',
            'QueueTimeOutURL': f'{self.timeout_url}/{timeout_url}',
            'Remarks': remarks,
            'Occasion': occasion
        }
        self.http_post(url, headers, payload)

    def http_post(self, url, headers, body):
        response = requests.post(url, headers=headers, json=body, verify=True)
        self.msg = response.text
        response.raise_for_status()
        return response.json()

    def env_url(self, request_url=None):
        base_url = self.sandbox_endpoint if self.env == 'sandbox' else self.live_endpoint
        return f'{base_url}{request_url}' if request_url else base_url

    def password(self):
        merchant_id = self.shortcode if self.transaction_type.lower() == 'paybill' else self.store_number
        return base64.b64encode(f'{merchant_id}{self.pass_key}{self.timestamp()}'.encode()).decode()

    def timestamp(self):
        return datetime.now().strftime('%Y%m%d%H%M%S')

    def security_credential_encryption(self):
        cert_file = 'ProductionCertificate.cer' if self.env == 'production' else 'SandboxCertificate.cer'
        with open(cert_file, 'rb') as cert:
            public_key = crypto.load_certificate(crypto.FILETYPE_PEM, cert.read())
            public_key = crypto.dump_publickey(crypto.FILETYPE_PEM, public_key)
        encrypted = crypto.sign(public_key, self.initiator_password, 'sha256')
        return base64.b64encode(encrypted).decode()

    def get_response_data(self, as_array=False):
        return self.msg if as_array else json.loads(self.msg)
