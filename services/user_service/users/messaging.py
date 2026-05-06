import json
import os
from decimal import Decimal

from user_service.settings import env

import pika

EXCHANGE = 'exposure'
QUEUE = 'user_service_queue'

_BINDINGS = (
    'store.created',       # promote BUYER → SELLER
    'payment.released',    # credit seller balance
)

RABBITMQ_URL = env('RABBITMQ_URL')


def _channel():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(
        exchange=EXCHANGE, exchange_type='topic', durable=True)
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

def publish_user_created(user):
    publish('user.created', {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
    })


def publish_user_updated(user):
    publish('user.updated', {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
    })


def publish_user_deleted(user_id):
    publish('user.deleted', {'user_id': user_id})


# --- Consumers ----------------------------------------------------------

def _handle_store_created(data):
    from users.models import User
    user_id = data.get('user_id')
    updated = User.objects.filter(
        id=user_id, role=User.Role.BUYER
    ).update(role=User.Role.SELLER)
    if updated:
        # Republish updated user so projections (social) see the new role.
        user = User.objects.get(id=user_id)
        publish_user_updated(user)
        print(f'[user] User {user_id} promoted to SELLER')


def _handle_payment_released(data):
    from users.models import SellerProfile
    seller_id = data.get('seller_id')
    amount = Decimal(str(data.get('amount', '0')))
    profile = SellerProfile.objects.filter(user_id=seller_id).first()
    if profile is None:
        print(f'[user] payment.released for unknown seller_id={seller_id}')
        return
    profile.balance = (profile.balance or 0) + amount
    profile.save(update_fields=['balance'])
    print(f'[user] credited seller {
          seller_id} +{amount} (balance now {profile.balance})')


def _on_message(ch, method, properties, body):
    routing_key = method.routing_key
    try:
        data = json.loads(body)
        if routing_key == 'store.created':
            _handle_store_created(data)
        elif routing_key == 'payment.released':
            _handle_payment_released(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f'[user] Failed to handle {routing_key}: {e}')
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumer():
    connection, channel = _channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    for routing_key in _BINDINGS:
        channel.queue_bind(exchange=EXCHANGE, queue=QUEUE,
                           routing_key=routing_key)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=_on_message)
    print('[user] Waiting for events...')
    channel.start_consuming()
