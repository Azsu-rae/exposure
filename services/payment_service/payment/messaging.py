import json
import os

import pika

EXCHANGE = 'exposure'
QUEUE = 'payment_service_queue'

_BINDINGS = (
    'delivery.status_changed',
)

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')


def _channel():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)
    return connection, channel


def publish(routing_key, payload):
    connection, channel = _channel()
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=routing_key,
        body=json.dumps(payload, default=str),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()


def publish_payment_released(payment):
    publish('payment.released', {
        'payment_id': payment.id,
        'order_id': str(payment.order_id),
        'seller_id': payment.seller_id,
        'amount': str(payment.amount),
    })


def publish_payment_refunded(payment):
    publish('payment.refunded', {
        'payment_id': payment.id,
        'order_id': str(payment.order_id),
        'buyer_id': payment.buyer_id,
        'amount': str(payment.amount),
    })


def _handle_delivery_status_changed(ch, method, properties, body):
    from payment.models import Payment

    data = json.loads(body)
    order_id = data.get('order_id')
    new_status = data.get('new_status')

    try:
        payment = Payment.objects.get(order_id=order_id)
    except Payment.DoesNotExist:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if new_status == 'Delivered' and payment.status in (Payment.Status.HELD, Payment.Status.PENDING):
        payment.status = Payment.Status.RELEASED
        from django.utils import timezone
        payment.release_date = timezone.now()
        payment.save(update_fields=['status', 'release_date'])
        publish_payment_released(payment)
        print(f'[payment] Order {order_id} → RELEASED')

    elif new_status == 'Cancelled' and payment.status == Payment.Status.HELD:
        payment.status = Payment.Status.REFUNDED
        payment.save(update_fields=['status'])
        publish_payment_refunded(payment)
        print(f'[payment] Order {order_id} → REFUNDED')

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    connection, channel = _channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    for routing_key in _BINDINGS:
        channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=routing_key)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=_handle_delivery_status_changed)
    print('[payment] Waiting for events...')
    channel.start_consuming()
