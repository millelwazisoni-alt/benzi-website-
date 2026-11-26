

import os
import django
import hmac
import hashlib

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings

body = b'{"payment_id":2,"event":"payment.succeeded"}'

signature = hmac.new(
    settings.PAYMENT_WEBHOOK_SECRET.encode(),
    body,
    hashlib.sha256
).hexdigest()

print(signature)
