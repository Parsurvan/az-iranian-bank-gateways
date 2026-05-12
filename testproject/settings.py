"""
Minimal Django settings for the az-iranian-bank-gateways sandbox.

Uses SQLite (no server needed).
MockBank is pre-configured with test.txt values so the full payment
lifecycle can be exercised without any real credentials.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "sandbox-insecure-key-do-not-use-in-production"

DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://bank.vicivm.online",
    "http://bank.vicivm.online",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "azbankgateways",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

# Required by Saman (SEP) gateway
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

ROOT_URLCONF = "testproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "sandbox.sqlite3"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── AZ Iranian Bank Gateways ───────────────────────────────────────────────
AZ_IRANIAN_BANK_GATEWAYS = {
    "GATEWAYS": {
        "MOCK": {
            # Probability (0-100) that verify() returns COMPLETE.
            # Set to 100 for always-success, 0 for always-cancel.
            "SUCCESS_RATE": 100,
            # Values taken from ~/test.txt (Iranian wire-transfer receipt)
            "SENDER_NAME":    "Alireza Golpaiganie / علیرضا گلبایگانی",
            "SENDER_BANK":    "Saderat Bank / بانک صادرات",
            "SENDER_SHEBA":   "IR050190000000021340642900",
            "RECEIVER_NAME":  "Mohammad Ali Dehghan Shorbaskhlo / محمدعلی دهقان شورباخلو",
            "RECEIVER_BANK":  "Refah Bank / بانک رفاه",
            "RECEIVER_SHEBA": "IR220130100000000078707870",
        },
        "SEP": {
            # Terminal created in irbankmock: parsvicci-testshop (ID=2)
            "MERCHANT_CODE": "2",
            "TERMINAL_CODE": "2",
            # Override real Saman URLs → point to irbankmock
            "TOKEN_API_URL":  "http://localhost:13000/banks/saman/OnlinePG/OnlinePG",
            "PAYMENT_URL":    "https://irbank.vicivm.online/banks/saman/OnlinePG/OnlinePG",
            "VERIFY_API_URL": "http://localhost:13000/banks/saman/verifyTxnRandomSessionkey/ipg/VerifyTransaction",
        },
    },
    "DEFAULT": "MOCK",
    "CURRENCY": "IRR",
    "TRACKING_CODE_LENGTH": 16,
    "TRACKING_CODE_QUERY_PARAM": "tc",
    "IS_SAMPLE_FORM_ENABLE": True,   # enables /bankgateways/sample-payment/
    "IS_SAFE_GET_GATEWAY_PAYMENT": False,
}
