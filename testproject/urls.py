from django.urls import path

from azbankgateways.urls import az_bank_gateways_urls

from . import views

urlpatterns = [
    path("pay/",    views.initiate_payment_view, name="initiate-payment"),
    path("result/", views.payment_result_view,   name="payment-result"),
    path("bankgateways/", az_bank_gateways_urls()),
]
