import json
import os

import pika

import delivery_service.settings as settings

EXCHANGE = 'exposure'
QUEUE = 'delivery_service_queue'

_BINDINGS = (
    'order.created',
)

RABBITMQ_URL = settings.env('RABBITMQ_URL', default='amqp://guest:guest@localhost:5672/')


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


def publish_delivery_status_changed(delivery):
    publish('delivery.status_changed', {
        'order_id': str(delivery.order_id),
        'delivery_id': delivery.pk,
        'new_status': delivery.delivery_status,
        'updated_at': delivery.updated_at.isoformat(),
    })


def _handle_order_created(ch, method, properties, body):
    """Project order.created into a PENDING Delivery row.

    Driver/company are left null until a dispatcher assigns one. This is
    the projection of "an order needs shipping" — Delivery still owns its
    own lifecycle from here on.
    """
    from delivery.models import Delivery

    data = json.loads(body)
    order_id = data['order_id']
    address = data.get('shipping_address') or ''

    Delivery.objects.get_or_create(
        order_id=order_id,
        defaults={'delivery_arrival_address': address},
    )
    print(f"[delivery] Delivery created for order {order_id}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    connection, channel = _channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    for routing_key in _BINDINGS:
        channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=routing_key)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=_handle_order_created)
    print('[delivery] Waiting for events...')
    channel.start_consuming()
