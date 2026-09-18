# mpesa_python
python library for mpesa 

##📦installation

git clone https://github.com/wasksofts-technology/mpesa_python.git
cd mpesa_python
pip install requests pyopenssl

##🚀 Usage
Import the library in your Python project:

python

```
from mpesa import Mpesa

mpesa = Mpesa()

# Environment: 'sandbox' or 'production'
mpesa.config('env', 'sandbox')

# API Credentials (from Safaricom Daraja Portal)
mpesa.config('consumer_key', 'YOUR_CONSUMER_KEY')
mpesa.config('consumer_secret', 'YOUR_CONSUMER_SECRET')

# Business Details
mpesa.config('shortcode', '174379')                  # Paybill / Till number
mpesa.config('store_number', '174379')               # Store number for Buy Goods
mpesa.config('pass_key', 'YOUR_LIPA_NA_MPESA_PASSKEY')
mpesa.config('transaction_type', 'paybill')          # 'paybill' or 'buygoods'

# URLs (must be HTTPS and publicly accessible)
mpesa.config('callback_url', 'https://yourdomain.com/callback')
mpesa.config('confirmation_url', 'https://yourdomain.com/confirmation')
mpesa.config('validation_url', 'https://yourdomain.com/validation')
mpesa.config('result_url', 'https://yourdomain.com/result')
mpesa.config('timeout_url', 'https://yourdomain.com/timeout')

# For Reversal API
mpesa.config('initiator_name', 'testapi')
mpesa.config('initiator_password', 'YOUR_INITIATOR_PASSWORD')
```
