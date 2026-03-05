from pretix.api.urls import event_router

from .api import X402PaymentViewSet

event_router.register('x402', X402PaymentViewSet, basename='event-x402')
