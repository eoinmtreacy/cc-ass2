
import pytest
import pika
import os
import time
from threading import Thread
from main import start_borrow_service
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope='module')
def rabbitmq_connection():
    rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER')
    rabbitmq_pass = os.getenv('RABBITMQ_DEFAULT_PASS')
    rabbitmq_host = os.getenv('RABBITMQ_HOST')

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    connection = pika.BlockingConnection(pika.ConnectionParameters(str(rabbitmq_host), 5672, "/", credentials))
    yield connection
    connection.close()

def test_rabbitmq_connection(rabbitmq_connection):
    assert rabbitmq_connection.is_open

def test_publish_and_consume_message(rabbitmq_connection):
    channel = rabbitmq_connection.channel()
    channel.queue_declare(queue='borrow_request')

    # Enable publisher confirms

    message = "Test Message"
    try:
        # Publish message and check for acknowledgment
        if channel.basic_publish(exchange='', routing_key='borrow_request', body=message):
            print(f" [x] Sent and acknowledged {message}")
        else:
            print(f" [x] Sent but not acknowledged {message}")
            assert False, "Message was not acknowledged"
    except pika.exceptions.UnroutableError:
        print(f" [x] Sent but not routable {message}")
        assert False, "Message was not routable"