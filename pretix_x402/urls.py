from django.urls import path

from . import api

urlpatterns = [
    path(
        'orders/<str:code>/payments/<int:local_id>/confirm_with_info/',
        api.confirm_with_payment_info,
        name='x402-confirm-with-info',
    ),
]
