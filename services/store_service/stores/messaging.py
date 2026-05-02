import json
import os

import pika

EXCHANGE = 'exposure'
QUEUE = 'store_service_queue'

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


# --- Producers ----------------------------------------------------------

def publish_order_created(order):
    publish('order.created', {
        'order_id': str(order.order_id),
        'user_id': order.user,
        'shipping_address': order.shipping_address,
        'payment_method': order.payment_method,
        'created_at': order.created_at.isoformat(),
    })


def publish_store_created(store):
    publish('store.created', {
        'store_id': store.id,
        'user_id': store.seller,
        'name': store.name,
        'wilaya': store.wilaya,
        'city': store.city,
        'rating': store.rating,
    })


def publish_store_updated(store):
    publish('store.updated', {
        'store_id': store.id,
        'user_id': store.seller,
        'name': store.name,
        'wilaya': store.wilaya,
        'city': store.city,
        'rating': store.rating,
    })


def publish_store_deleted(store_id):
    publish('store.deleted', {'store_id': store_id})


def publish_product_created(product):
    publish('product.created', {
        'product_id': product.id,
        'store_id': product.store_id,
        'name': product.name,
        'price': str(product.price),
        'category': product.category,
    })


def publish_product_updated(product):
    publish('product.updated', {
        'product_id': product.id,
        'store_id': product.store_id,
        'name': product.name,
        'price': str(product.price),
        'category': product.category,
    })


def publish_product_deleted(product_id):
    publish('product.deleted', {'product_id': product_id})


# --- Consumer -----------------------------------------------------------

# Order status mirrors only terminal delivery states. Intermediate states
# (Accepted, In Transit) are visible directly via the delivery service.
_DELIVERY_TO_ORDER = {
    'Delivered': 'Confirmed',
    'Cancelled': 'Cancelled',
}


def _handle_delivery_status_changed(ch, method, properties, body):
    from stores.models import Order
    data = json.loads(body)
    order_id = data.get('order_id')
    new_status = data.get('new_status')

    target = _DELIVERY_TO_ORDER.get(new_status)
    if target:
        updated = Order.objects.filter(order_id=order_id).update(status=target)
        if updated:
            print(f'[store] Order {order_id} → {target}')

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    connection, channel = _channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    for routing_key in _BINDINGS:
        channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=routing_key)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=_handle_delivery_status_changed)
    print('[store] Waiting for events...')
    channel.start_consuming()
