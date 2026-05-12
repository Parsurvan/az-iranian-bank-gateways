from django.urls import path

from . import default_settings as settings
from .apps import AZIranianBankGatewaysConfig
from .views import (
    callback_view,
    go_to_bank_gateway,
    mock_bank_gateway_view,
    mock_outcome_view,
    sample_payment_view,
    sample_result_view,
)

app_name = AZIranianBankGatewaysConfig.name

_urlpatterns = [
    path("callback/", callback_view, name="callback"),
]

if not settings.IS_SAFE_GET_GATEWAY_PAYMENT:
    _urlpatterns += [
        path("go-to-bank-gateway/", go_to_bank_gateway, name="go-to-bank-gateway"),
    ]

if settings.IS_SAMPLE_FORM_ENABLE:
    _urlpatterns += [
        path("sample-payment/", sample_payment_view, name="sample-payment"),
        path("sample-result/", sample_result_view, name="sample-result"),
    ]

_urlpatterns += [
    path("mock-outcome/", mock_outcome_view, name="mock-outcome"),
    path("mock-bank-gateway/", mock_bank_gateway_view, name="mock-bank-gateway"),
]


def az_bank_gateways_urls():
    return _urlpatterns, app_name, app_name
