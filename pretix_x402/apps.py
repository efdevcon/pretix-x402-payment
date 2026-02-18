from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class X402App(AppConfig):
    name = "pretix_x402"
    verbose_name = "x402 Crypto Payment"

    class PretixPluginMeta:
        name = _("x402 Crypto Payment")
        author = "Devcon"
        category = "PAYMENT"
        description = _(
            "Displays on-chain crypto payment details (tx hash, chain, token, payer) "
            "for orders placed via the x402 payment protocol."
        )
        visible = True
        version = "0.1.0"

    def ready(self):
        from . import signals  # noqa: F401
