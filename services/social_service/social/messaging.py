import json
import os

import pika

from .models import UserRef, StoreRef, ProductRef

EXCHANGE = 'exposure'
QUEUE = 'social_service_queue'

# Read model: subscribe to anything that changes the entities we display.
_BINDINGS = (
    'user.created', 'user.updated', 'user.deleted',
    'store.created', 'store.updated', 'store.deleted',
    'product.created', 'product.updated', 'product.deleted',
)

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')


def _channel():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)
    return connection, channel


# --- Handlers -----------------------------------------------------------

def _upsert_user(data):
    UserRef.objects.update_or_create(
        id=data['user_id'],
        defaults={
            'username': data.get('username', ''),
            'role': data.get('role', ''),
        },
    )


def _upsert_store(data):
    StoreRef.objects.update_or_create(
        id=data['store_id'],
        defaults={
            'seller_id': data.get('user_id') or data.get('seller_id'),
            'name': data.get('name', ''),
            'wilaya': data.get('wilaya', ''),
            'city': data.get('city', ''),
            'rating': data.get('rating', 0.0),
        },
    )


def _upsert_product(data):
    ProductRef.objects.update_or_create(
        id=data['product_id'],
        defaults={
            'store_id': data['store_id'],
            'name': data.get('name', ''),
            'price': data.get('price', 0),
            'category': data.get('category', 'General'),
        },
    )


def _on_message(ch, method, properties, body):
    routing_key = method.routing_key
    try:
        data = json.loads(body)
        if routing_key == 'user.created' or routing_key == 'user.updated':
            _upsert_user(data)
        elif routing_key == 'user.deleted':
            UserRef.objects.filter(id=data['user_id']).delete()
        elif routing_key == 'store.created' or routing_key == 'store.updated':
            _upsert_store(data)
        elif routing_key == 'store.deleted':
            StoreRef.objects.filter(id=data['store_id']).delete()
        elif routing_key == 'product.created' or routing_key == 'product.updated':
            _upsert_product(data)
        elif routing_key == 'product.deleted':
            ProductRef.objects.filter(id=data['product_id']).delete()
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # Reject without requeue so a poison message doesn't loop forever.
        # In production this should go to a DLX; for now it's logged.
        print(f'[social] Failed to handle {routing_key}: {e}')
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumer():
    connection, channel = _channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    for routing_key in _BINDINGS:
        channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=routing_key)
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(queue=QUEUE, on_message_callback=_on_message)
    print('[social] Waiting for events...')
    channel.start_consuming()
