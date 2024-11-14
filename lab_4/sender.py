import pika
credentials = pika.PlainCredentials("guest", "guest")
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", 5672, "/", credentials))
channel = connection.channel()
channel.basic_publish(exchange='',routing_key='hello',body='Hello Rabbit!')
print(" [x] Sent 'Hello Rabbit!'")
connection.close()