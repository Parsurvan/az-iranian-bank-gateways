"""
MockBank — a first-class BankType.MOCK implementation of BaseBank.

It never contacts an external server.  All required values (reference
number, tracking code, …) are generated locally with uuid / random so
the full Django payment lifecycle can be exercised from outside Iran.

Config keys accepted in AZ_IRANIAN_BANK_GATEWAYS['GATEWAYS']['MOCK']:
    SUCCESS_RATE   int 0-100  probability that verify() succeeds (default 100)
    SENDER_NAME    str        shown on the mock bank gateway page (optional)
    SENDER_BANK    str        idem
    SENDER_SHEBA   str        idem
    RECEIVER_NAME  str        idem
    RECEIVER_BANK  str        idem
    RECEIVER_SHEBA str        idem

Flow:
  1. factory.create(BankType.MOCK) → MockBank instance
  2. bank.ready()                  → pays (generates ref + tc), writes Bank row
  3. bank.redirect_gateway()       → GET /azbankgateways/go-to-bank-gateway/
                                      → GET /azbankgateways/mock-bank-gateway/
  4. User clicks "Confirm" or "Cancel" on that page
  5. Browser lands on /azbankgateways/callback/?bank_type=MOCK&…
  6. verify_from_gateway()         → reads mock_status param, sets COMPLETE / CANCEL
  7. redirect_client_callback()    → your result view (?tc=<tracking_code>)
"""

import logging
import random
import uuid

from azbankgateways.banks.banks import BaseBank
from azbankgateways.models import BankType, PaymentStatus


class MockBank(BaseBank):
    """Sandbox bank gateway — works everywhere, needs no network calls."""

    # ── optional config ────────────────────────────────────────────────────
    _success_rate: int = 100
    _sender_name: str = ""
    _sender_bank: str = ""
    _sender_sheba: str = ""
    _receiver_name: str = ""
    _receiver_bank: str = ""
    _receiver_sheba: str = ""

    # ── internal state set by prepare_verify_from_gateway ─────────────────
    _mock_confirmed: bool = True

    # ──────────────────────────────────────────────────────────────────────
    def set_default_settings(self):
        """Read optional config keys; nothing is mandatory for the mock."""
        cfg = self.default_setting_kwargs
        self._success_rate = int(cfg.get("SUCCESS_RATE", 100))
        self._sender_name  = cfg.get("SENDER_NAME",   "")
        self._sender_bank  = cfg.get("SENDER_BANK",   "")
        self._sender_sheba = cfg.get("SENDER_SHEBA",  "")
        self._receiver_name  = cfg.get("RECEIVER_NAME",  "")
        self._receiver_bank  = cfg.get("RECEIVER_BANK",  "")
        self._receiver_sheba = cfg.get("RECEIVER_SHEBA", "")

    def get_bank_type(self):
        return BankType.MOCK

    # ── skip gateway-token expiry for the sandbox ──────────────────────────
    def _verify_payment_expiry(self):
        logging.debug("MockBank: gateway token expiry check skipped.")

    # ── pay ────────────────────────────────────────────────────────────────
    def prepare_pay(self):
        super().prepare_pay()

    def get_pay_data(self):
        return {
            "tracking_code": self.get_tracking_code(),
            "amount": self.get_gateway_amount(),
        }

    def pay(self):
        super().pay()
        ref = uuid.uuid4().hex.upper()
        self._set_reference_number(ref)
        self._set_transaction_status_text("Mock payment initiated.")
        logging.debug("MockBank: generated reference_number=%s", ref)

    # ── gateway redirect params ────────────────────────────────────────────
    def _get_gateway_payment_url_parameter(self):
        """The 'bank URL' is our own local mock gateway page."""
        from django.urls import reverse
        from azbankgateways.apps import AZIranianBankGatewaysConfig
        app = AZIranianBankGatewaysConfig.name
        return reverse(f"{app}:mock-bank-gateway")

    def _get_gateway_payment_parameter(self):
        return {
            "tc":            str(self.get_tracking_code()),
            "amount":        str(self.get_gateway_amount()),
            "callback":      self._get_gateway_callback_url(),
            "sender":        self._sender_name,
            "sender_bank":   self._sender_bank,
            "receiver":      self._receiver_name,
            "receiver_bank": self._receiver_bank,
        }

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    # ── verify ────────────────────────────────────────────────────────────
    def prepare_verify_from_gateway(self):
        super().prepare_verify_from_gateway()
        req = self.get_request()
        raw_status = req.GET.get("mock_status", "SUCCESS").upper()
        self._mock_confirmed = (raw_status == "SUCCESS")
        tc = req.GET.get("tc")
        if tc:
            self._set_tracking_code(tc)
        self._set_bank_record()

    def get_verify_data(self):
        return {
            "tracking_code": self.get_tracking_code(),
            "mock_confirmed": self._mock_confirmed,
        }

    def prepare_verify(self, tracking_code):
        super().prepare_verify(tracking_code)

    def verify(self, tracking_code):
        super().verify(tracking_code)
        if self._mock_confirmed and random.randint(1, 100) <= self._success_rate:
            self._set_payment_status(PaymentStatus.COMPLETE)
            self._set_transaction_status_text("Mock payment verified and completed.")
            logging.debug("MockBank: payment COMPLETE tc=%s", tracking_code)
        elif not self._mock_confirmed:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            self._set_transaction_status_text("User cancelled the mock payment.")
            logging.debug("MockBank: payment CANCELLED BY USER tc=%s", tracking_code)
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            self._set_transaction_status_text(
                f"Mock bank rejected payment (SUCCESS_RATE={self._success_rate}%)."
            )
            logging.debug("MockBank: payment REJECTED (rate) tc=%s", tracking_code)
