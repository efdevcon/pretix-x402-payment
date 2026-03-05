from django.dispatch import receiver
from django.urls import path

try:
    from pretix.base.signals import register_payment_providers
except ImportError:
    register_payment_providers = None

try:
    from pretix.api.signals import register_api_urls
except ImportError:
    register_api_urls = None


if register_payment_providers is not None:

    @receiver(register_payment_providers, dispatch_uid="payment_x402")
    def register_payment_provider(sender, **kwargs):
        from .payment import X402CryptoPayment

        return X402CryptoPayment


if register_api_urls is not None:

    @receiver(register_api_urls, dispatch_uid="api_x402")
    def register_api_url(sender, **kwargs):
        from . import api

        return [
            path(
                'orders/<str:code>/payments/<int:local_id>/confirm_with_info/',
                api.confirm_with_payment_info,
                name='x402-confirm-with-info',
            ),
        ]
