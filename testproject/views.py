"""
Test project views:
  /pay/     → initiates a MockBank payment and redirects to the mock gateway
  /result/  → shows the outcome.html receipt after returning from the gateway
"""

import logging

from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from azbankgateways import bankfactories, default_settings as settings
from azbankgateways import models as bank_models
from azbankgateways.exceptions import AZBankGatewaysException


def initiate_payment_view(request):
    """Create a MockBank payment and redirect the user to the sandbox gateway."""
    amount = int(request.GET.get("amount", 50_000_000_000))  # default: test.txt amount

    factory = bankfactories.BankFactory()
    try:
        bank = factory.create(bank_models.BankType.MOCK)
        bank.set_request(request)
        bank.set_amount(amount)
        bank.set_client_callback_url(
            request.build_absolute_uri(reverse("payment-result"))
        )
        bank.ready()
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical("MockBank init error: %s", e)
        return HttpResponse(f"<h2>Error: {e}</h2>", status=500)


def initiate_sep_payment_view(request):
    """Create a SEP (Saman) payment via irbankmock and redirect the user."""
    amount = int(request.GET.get("amount", 50_000_000_000))

    factory = bankfactories.BankFactory()
    try:
        bank = factory.create(bank_models.BankType.SEP)
        bank.set_request(request)
        bank.set_amount(amount)
        bank.set_client_callback_url(
            request.build_absolute_uri(reverse("payment-result"))
        )
        bank.ready()
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical("SEP init error: %s", e)
        return HttpResponse(f"<h2>Error: {e}</h2>", status=500)


def payment_result_view(request):
    """Verify the payment and render the custom outcome template."""
    tc = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM)
    if not tc:
        raise Http404("No tracking code provided.")

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tc)
    except bank_models.Bank.DoesNotExist:
        raise Http404("Payment record not found.")

    from django.shortcuts import render
    return render(
        request,
        "azbankgateways/outcome.html",
        {
            "bank_record": bank_record,
            "is_mock": True,
            "pay_again_url": reverse("initiate-payment"),
        },
    )
