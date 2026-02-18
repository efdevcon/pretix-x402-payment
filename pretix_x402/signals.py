from django.dispatch import receiver

try:
    from pretix.base.signals import register_payment_providers
except ImportError:
    register_payment_providers = None


if register_payment_providers is not None:

    @receiver(register_payment_providers, dispatch_uid="payment_x402")
    def register_payment_provider(sender, **kwargs):
        from .payment import X402CryptoPayment

        return X402CryptoPayment
