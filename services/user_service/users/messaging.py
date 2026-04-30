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


def _handle_store_created(ch, method, properties, body):
    from users.models import User
    data = json.loads(body)
    user_id = data.get('user_id')

    updated = User.objects.filter(id=user_id, role=User.Role.BUYER).update(role=User.Role.SELLER)
    if updated:
        print(f'[user] User {user_id} promoted to SELLER')

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    connection, channel = _channel()
    channel.queue_declare(queue='user_service_queue', durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue='user_service_queue', routing_key='store.created')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='user_service_queue', on_message_callback=_handle_store_created)
    print('[user] Waiting for events...')
    channel.start_consuming()
