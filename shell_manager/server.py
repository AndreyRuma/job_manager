import pika
import subprocess
import os


class RecladaJMServer():
    def __init__(self):

        host = os.getenv("RECLADA_RABBITMQ_HOST", "localhost")
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue='reclada_rpc_queue')
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(queue='reclada_rpc_queue', on_message_callback=self.on_request)

    def handle_request(self, body):
        body = body.decode("utf-8")
        print(f'request: {body}')
        try:
            self._process = subprocess.run(body, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        except Exception as ex:
            response = format(ex)
            return response

        output = self._process.stdout
        error = self._process.stderr
        response = error if error else output
        response = f"{response.decode('utf-8')}"
        return response

    def on_request(self, ch, method, props, body):
        response = self.handle_request(body)
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id= \
                                                         props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self._channel.start_consuming()


reclada_jm = RecladaJMServer()
print(" [x] Awaiting requests")
reclada_jm.start()