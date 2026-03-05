import inspect

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from pretix.base.models import OrderPayment


class X402PaymentViewSet(viewsets.ViewSet):
    """Custom API endpoints for x402 crypto payments."""

    @action(detail=False, methods=['POST'], url_path='confirm/(?P<code>[^/]+)/(?P<local_id>[0-9]+)')
    def confirm_payment(self, request, code=None, local_id=None, **kwargs):
        """
        Confirm a payment with payment info rendered into the confirmation email.

        POST /api/v1/organizers/{org}/events/{event}/x402/confirm/{code}/{local_id}/
        """
        try:
            order = request.event.orders.get(code=code)
        except request.event.orders.model.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            payment = order.payments.get(local_id=local_id)
        except OrderPayment.DoesNotExist:
            return Response({'detail': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        if payment.state not in (OrderPayment.PAYMENT_STATE_PENDING, OrderPayment.PAYMENT_STATE_CREATED):
            return Response({'detail': 'Invalid payment state'}, status=status.HTTP_400_BAD_REQUEST)

        force = request.data.get('force', False)
        send_mail = request.data.get('send_email', True)

        # Update payment info if provided
        info_str = request.data.get('info')
        if info_str:
            import json
            payment.info = info_str if isinstance(info_str, str) else json.dumps(info_str)
            payment.save(update_fields=['info'])
            payment.refresh_from_db()

        # Render payment info for the email via order_pending_mail_render
        mail_text = ''
        try:
            provider = payment.payment_provider
            if hasattr(provider, 'order_pending_mail_render'):
                sig = inspect.signature(provider.order_pending_mail_render)
                if 'payment' in sig.parameters:
                    mail_text = str(provider.order_pending_mail_render(order, payment))
                else:
                    mail_text = str(provider.order_pending_mail_render(order))
        except Exception:
            pass

        try:
            payment.confirm(
                auth=request.auth,
                count_waitinglist=False,
                send_mail=send_mail,
                force=force,
                mail_text=mail_text,
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'state': payment.state}, status=status.HTTP_200_OK)
