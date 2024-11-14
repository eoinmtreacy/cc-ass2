import pika, sys, os



def main():
    
    rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER')
    rabbitmq_pass = os.getenv('RABBITMQ_DEFAULT_PASS')
    rabbitmq_host = os.getenv('RABBITMQ_HOST')

    print(rabbitmq_user, rabbitmq_pass, rabbitmq_host)

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, 5672, "/", credentials))
        channel = connection.channel()
        channel.queue_declare(queue='borrow_request')
        print("Borrow service waiting for requests on", str(rabbitmq_host) + "/5672")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    def callback(ch, method, properties, body):
        print(f"Received {body}")

    channel.basic_consume(queue='borrow_request', on_message_callback=callback, auto_ack=False)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)