import base64
import json
import os

import pika
from django.db import close_old_connections

from .models import UserRef, StoreRef, ProductRef

EXCHANGE = 'exposure'
QUEUE = 'social_service_queue'

# Read model: subscribe to anything that changes the entities we display,
# plus the verdicts coming back from the moderation service.
_BINDINGS = (
    'user.created', 'user.updated', 'user.deleted',
    'store.created', 'store.updated', 'store.deleted',
    'product.created', 'product.updated', 'product.deleted',
    'image.moderation.completed',
)

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')


def _channel():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)
    return connection, channel


# --- Producers ----------------------------------------------------------

def publish(routing_key, payload):
    connection, channel = _channel()
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=routing_key,
        body=json.dumps(payload, default=str),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()


def publish_image_moderation_requested(post_id, image_bytes, content_type='', filename=''):
    """
    Ask the moderation service to scan a post's image.

    The image bytes travel inside the message itself (base64-encoded), so
    the producer and consumer don't have to share a filesystem. Trade-off:
    the broker carries the payload, so keep an eye on message size if you
    ever accept big uploads. Swap to an object-store reference (S3 key,
    signed URL) once that becomes a problem.
    """
    publish('image.moderation.requested', {
        'post_id': post_id,
        'image_b64': base64.b64encode(image_bytes).decode('ascii'),
        'content_type': content_type,
        'filename': filename,
    })


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


def _apply_moderation_verdict(data):
    from .models import Post
    post_id = data.get('post_id')
    approved = data.get('approved', True)
    reason = data.get('reason', '')
    new_status = (
        Post.ModerationStatus.APPROVED if approved
        else Post.ModerationStatus.REJECTED
    )
    updated = Post.objects.filter(id=post_id).update(
        moderation_status=new_status,
        moderation_reason=reason,
    )
    if updated:
        print(f'[social] post {post_id} -> {new_status} ({reason!r})')
    else:
        print(f'[social] moderation verdict for unknown post {post_id}')


def _on_message(ch, method, properties, body):
    routing_key = method.routing_key
    # Drop any stale DB connections before touching the ORM. A long-running
    # consumer has no request lifecycle, so Django never refreshes them on
    # its own — without this, the first query after a Postgres-side timeout
    # blows up with "server closed the connection unexpectedly".
    close_old_connections()
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
        elif routing_key == 'image.moderation.completed':
            _apply_moderation_verdict(data)
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
