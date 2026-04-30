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


def publish_delivery_status_changed(delivery):
    publish('delivery.status_changed', {
        'order_id': str(delivery.order_id),
        'delivery_id': delivery.pk,
        'new_status': delivery.delivery_status,
        'updated_at': delivery.updated_at.isoformat(),
    })


def _handle_order_created(ch, method, properties, body):
    data = json.loads(body)
    print(f"[delivery] order.created received: order_id={data.get('order_id')} user_id={data.get('user_id')}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    connection, channel = _channel()
    channel.queue_declare(queue='delivery_service_queue', durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue='delivery_service_queue', routing_key='order.created')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='delivery_service_queue', on_message_callback=_handle_order_created)
    print('[delivery] Waiting for events...')
    channel.start_consuming()
