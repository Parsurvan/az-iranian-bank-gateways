"""
mock_outcome.py — Render `outcome.html` with synthetic (mock) Bank data.

This is intentionally outside the normal payment flow so the template can
be previewed / developed without a live Iranian bank gateway.

Usage (add to your project's urls.py while developing):
    from azbankgateways.views import mock_outcome_view
    path("mock-outcome/", mock_outcome_view, name="mock-outcome"),

Query-string params (all optional):
    ?status=COMPLETE                       — any PaymentStatus value
    ?bank=SADERAT                          — any BankType value (or free-form label)
    ?amount=50000000000                    — integer IRR amount
    ?tracking_code=IR220130100000000078707870
    ?reference_number=IR050190000000021340642900
    ?response_result=Transaction+processed
    ?extra_information={"key":"value"}     — raw JSON shown in the extra box
    ?sender=Alireza+Golpaiganie
    ?receiver=Mohammad+Ali+Dehghan
    ?receiver_bank=REFAH+BANK
    ?identifier=saderat-1
"""

import json
import types

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from azbankgateways.models import BankType, PaymentStatus

_ALL_STATUSES = [
    PaymentStatus.WAITING,
    PaymentStatus.REDIRECT_TO_BANK,
    PaymentStatus.RETURN_FROM_BANK,
    PaymentStatus.COMPLETE,
    PaymentStatus.CANCEL_BY_USER,
    PaymentStatus.EXPIRE_GATEWAY_TOKEN,
    PaymentStatus.EXPIRE_VERIFY_PAYMENT,
    PaymentStatus.ERROR,
]

_KNOWN_BANK_TYPES = {bt.value for bt in BankType}


def _make_mock_record(
    *,
    status: str,
    bank_type: str,
    amount: int,
    tracking_code: str,
    reference_number: str,
    response_result: str,
    extra_information: str,
    callback_url: str,
    identifier: str,
) -> types.SimpleNamespace:
    """Return a duck-typed object that matches what outcome.html expects."""
    return types.SimpleNamespace(
        pk=9999,
        bank_type=bank_type,
        status=status,
        amount=str(amount),
        tracking_code=tracking_code,
        reference_number=reference_number,
        response_result=response_result,
        extra_information=extra_information,
        callback_url=callback_url,
        bank_choose_identifier=identifier,
        created_at=timezone.now(),
        is_success=(status == PaymentStatus.COMPLETE),
    )


def mock_outcome_view(request):
    """Render the custom outcome template with mock (or custom) data."""
    g = request.GET

    # ── Status ──────────────────────────────────────────────────────────────
    raw_status = g.get("status", PaymentStatus.COMPLETE).upper()
    valid_statuses = {s.value for s in _ALL_STATUSES}
    status = raw_status if raw_status in valid_statuses else PaymentStatus.COMPLETE

    # ── Bank type (allow free-form labels like "SADERAT", "REFAH") ──────────
    bank_type = g.get("bank", "ZARINPAL").upper()

    # ── Amount ───────────────────────────────────────────────────────────────
    try:
        amount = int(g.get("amount", 150_000))
    except (ValueError, TypeError):
        amount = 150_000

    # ── Custom overridable fields ─────────────────────────────────────────
    tracking_code = g.get("tracking_code", "IR220130100000000078707870")
    reference_number = g.get("reference_number", "IR050190000000021340642900")

    is_success = status == PaymentStatus.COMPLETE
    default_response = "Transfer confirmed by bank" if is_success else "Payment not confirmed"
    response_result = g.get("response_result", default_response)

    # Build extra_information JSON from sender/receiver params or raw override
    if "extra_information" in g:
        extra_information = g["extra_information"]
    else:
        extra = {}
        if g.get("sender"):
            extra["sender"] = g["sender"]
        if g.get("receiver"):
            extra["receiver"] = g["receiver"]
        if g.get("receiver_bank"):
            extra["receiver_bank"] = g["receiver_bank"]
        if g.get("sender_sheba"):
            extra["sender_sheba"] = g["sender_sheba"]
        if g.get("receiver_sheba"):
            extra["receiver_sheba"] = g["receiver_sheba"]
        extra_information = json.dumps(extra, ensure_ascii=False, indent=2) if extra else ""

    callback_url = g.get("callback_url", "/")
    identifier = g.get("identifier", "mock-1")

    # ── Index page when no params given ──────────────────────────────────────
    if "status" not in g:
        links = []
        for s in _ALL_STATUSES:
            for b in [BankType.ZARINPAL, BankType.MELLAT, BankType.SEP]:
                links.append(
                    f'<a href="?status={s.value}&bank={b.value}&amount=150000">'
                    f"{s.value} / {b.value}</a>"
                )
        nav = (
            "<html><head><title>Mock Outcome Index</title>"
            "<style>body{font:14px monospace;background:#0f172a;color:#94a3b8;padding:2rem}"
            "a{color:#60a5fa;display:block;margin:.25rem 0}</style></head>"
            "<body><h2 style='color:#e2e8f0;margin-bottom:1rem'>Mock Outcome States</h2>"
            + "\n".join(links)
            + "</body></html>"
        )
        return HttpResponse(nav)

    bank_record = _make_mock_record(
        status=status,
        bank_type=bank_type,
        amount=amount,
        tracking_code=tracking_code,
        reference_number=reference_number,
        response_result=response_result,
        extra_information=extra_information,
        callback_url=callback_url,
        identifier=identifier,
    )

    return render(
        request,
        "azbankgateways/outcome.html",
        {"bank_record": bank_record, "is_mock": True},
    )
