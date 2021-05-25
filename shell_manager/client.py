import pika
import uuid
import os

class ReclalaJMClient(object):

    def __init__(self):
        host = os.getenv("RECLADA_RABBITMQ_HOST", "91.122.49.27")
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, command):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='reclada_rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=command)
        while self.response is None:
            self.connection.process_data_events()
        return self.response


if __name__ == "__main__":
    jm_client = ReclalaJMClient()
    while True:
        rpc_command = input("jm@")
        response = jm_client.call(rpc_command)
        response = response.decode("utf-8")
        output = response
        print(f"{response}")