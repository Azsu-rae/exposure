import json
import os
import pika

EXCHANGE = 'exposure'
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
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()


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
    })


def _handle_delivery_status_changed(ch, method, properties, body):
    from stores.models import Order
    data = json.loads(body)
    order_id = data.get('order_id')
    new_status = data.get('new_status')

    status_map = {
        'Delivered': Order.StatusChoices.CONFIRMED,
        'Cancelled': Order.StatusChoices.CANCELLED,
    }

    if new_status in status_map:
        updated = Order.objects.filter(order_id=order_id).update(status=status_map[new_status])
        if updated:
            print(f'[store] Order {order_id} → {status_map[new_status]}')

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    connection, channel = _channel()
    channel.queue_declare(queue='store_service_queue', durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue='store_service_queue', routing_key='delivery.status_changed')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='store_service_queue', on_message_callback=_handle_delivery_status_changed)
    print('[store] Waiting for events...')
    channel.start_consuming()
