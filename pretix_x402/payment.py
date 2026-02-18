from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from pretix.base.payment import BasePaymentProvider


# Chain ID → (explorer base URL, display name)
CHAIN_INFO = {
    1: ("https://etherscan.io", "Ethereum"),
    10: ("https://optimistic.etherscan.io", "Optimism"),
    137: ("https://polygonscan.com", "Polygon"),
    42161: ("https://arbiscan.io", "Arbitrum"),
    8453: ("https://basescan.org", "Base"),
    84532: ("https://sepolia.basescan.org", "Base Sepolia"),
    11155111: ("https://sepolia.etherscan.io", "Sepolia"),
    80002: ("https://amoy.polygonscan.com", "Polygon Amoy"),
}


class X402CryptoPayment(BasePaymentProvider):
    """
    Minimal payment provider for orders paid via the x402 crypto payment protocol.

    This provider does NOT handle checkout — orders are created and marked paid
    through the API. Its sole purpose is to store and display on-chain payment
    details (tx hash, chain, token, payer wallet) in the Pretix admin backend.
    """

    identifier = "x402_crypto"
    verbose_name = _("x402 Crypto")
    public_name = _("Crypto (x402)")

    def is_allowed(self, request, total=None):
        # This provider is only used programmatically via the API,
        # never shown in Pretix's own checkout flow.
        return False

    def payment_is_valid_session(self, request):
        return False

    def payment_control_render(self, request, payment):
        """Render payment details in the Pretix admin order view."""
        info = payment.info_data or {}
        chain_id = info.get("chain_id")
        explorer_base, chain_name = CHAIN_INFO.get(chain_id, (None, None))

        tx_hash = info.get("tx_hash", "")
        tx_url = f"{explorer_base}/tx/{tx_hash}" if explorer_base and tx_hash else None

        payer = info.get("payer", "")
        payer_url = f"{explorer_base}/address/{payer}" if explorer_base and payer else None

        template = get_template("pretix_x402/control.html")
        return template.render(
            {
                "info": info,
                "tx_url": tx_url,
                "payer_url": payer_url,
                "chain_name": chain_name or info.get("network", f"Chain {chain_id}"),
            }
        )

    def payment_control_render_short(self, payment):
        """Short one-line identifier shown in admin order lists."""
        info = payment.info_data or {}
        tx = info.get("tx_hash", "")
        symbol = info.get("token_symbol", "crypto")
        if tx:
            return f"{symbol} — {tx[:10]}…{tx[-6:]}"
        return symbol
