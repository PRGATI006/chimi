"""
WSGI config for Certificate Fraud Detection project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certificate_fraud_detection.settings')

application = get_wsgi_application()
