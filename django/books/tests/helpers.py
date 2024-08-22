import pika
import os
import json
from django.conf import settings

def publish_message(message, exchange, routing_key, content_type, queue):
    """
    Publish a message to a RabbitMQ exchange and ensure the message is routed to the specified queue.

    Args:
        message (dict): The message to send in dictionary format.
        exchange (str): The exchange to publish the message to.
        routing_key (str): The routing key to use for the message.
        content_type (str): The content type of the message.
        queue (str): The queue to bind to the exchange with the routing key.
    """
    # Retrieve RabbitMQ credentials from environment variables
    rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "mazimi")
    rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS", "mazimi")
    rabbitmq_host = 'rabbitmq'  # Or the Docker container name if running in Docker
    rabbitmq_port = 5672  # The port RabbitMQ is listening on

    # Create credentials object
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)

    # Establish a connection to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=credentials
        )
    )
    channel = connection.channel()

    # Declare the exchange with durable=True to match the existing properties
    channel.exchange_declare(
        exchange=exchange,
        exchange_type='direct',
        durable=True  # Ensure this matches the existing exchange properties
    )

    # Declare the queue with durable=True to match the existing properties
    channel.queue_declare(
        queue=queue,
        durable=True  # Ensure this matches the existing queue properties
    )

    # Bind the queue to the exchange with the specified routing key
    channel.queue_bind(
        exchange=exchange,
        queue=queue,
        routing_key=routing_key
    )

    # Convert the message dictionary to a JSON string
    json_message = json.dumps(message)

    # Publish the message to the exchange with the specified routing key and content type
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json_message,
        properties=pika.BasicProperties(
            content_type=content_type
        )
    )
    # Close the connection
    connection.close()


def delete_cache(book_id, caches=None):
    if caches is None:
        caches = list(settings.CACHES.keys())
    message = {
        "task": "books.tasks.clear_book_cache",
        "id": "1",
        "kwargs": {
            "book_id": book_id,
            "delete_from": caches
        },
        "retries": 0
    }
    exchange = 'books'
    routing_key = 'books.clear_cache'
    content_type = 'application/json'
    queue = 'cache_cleaner'
    publish_message(message, exchange, routing_key, content_type, queue)

def refresh_caches(book_id,caches=None):
    if caches is None:
        caches = list(settings.CACHES.keys())
    message = {
        "task": "books.tasks.refresh_book_cache",
        "id": "1",
        "kwargs": {
            "book_id": book_id,
            "update_in": caches
        },
        "retries": 0
    }
    exchange = 'books'
    routing_key = 'books.refresh_cache'
    content_type = 'application/json'
    queue = 'cache_cleaner'
    publish_message(message, exchange, routing_key, content_type, queue)