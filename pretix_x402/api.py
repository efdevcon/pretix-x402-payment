from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pretix.api.auth.permission import EventPermission
from pretix.base.models import OrderPayment
from pretix.base.services.quotas import QuotaAvailability


@api_view(['POST'])
@permission_classes([EventPermission])
def confirm_with_payment_info(request, organizer, event, code, local_id):
    """
    Custom confirm endpoint that renders payment info into the confirmation email.

    Wraps payment.confirm() and passes mail_text generated from order_pending_mail_render
    so that {payment_info} is populated in the "payment received" email template.
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

    # Update info if provided
    info_data = request.data.get('info')
    if info_data:
        import json
        payment.info = info_data if isinstance(info_data, str) else json.dumps(info_data)
        payment.save(update_fields=['info'])

    # Render payment info for the email
    mail_text = ''
    try:
        provider = payment.payment_provider
        if hasattr(provider, 'order_pending_mail_render'):
            import inspect
            sig = inspect.signature(provider.order_pending_mail_render)
            if 'payment' in sig.parameters:
                mail_text = str(provider.order_pending_mail_render(order, payment))
            else:
                mail_text = str(provider.order_pending_mail_render(order))
    except Exception:
        pass  # Fall back to empty mail_text

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
