from typing import List

from kafka import KafkaProducer, KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord

# https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka : To understand Aiven's Apache Kafka
# https://help.aiven.io/en/articles/5343895-python-examples-for-testing-aiven-for-apache-kafka : to do a Python Kafka producer and consumer implementation

class Producer:
    """
    Kafka producer to produce messages
    """
    def __init__(self, server: str, topic: str):
        self.server = server
        self.topic = topic

        try:
            self.producer = KafkaProducer(
                    bootstrap_servers=self.server,
                    security_protocol="SSL",
                    ssl_cafile="auth/ca.pem",
                    ssl_certfile="auth/service.cert",
                    ssl_keyfile="auth/service.key"
            )
        except Exception as e:
            print(f'Error connecting to Kafka broker: {e}')
            raise e

    def produce(self, message: bytes):
        self.producer.send(self.topic, message)


class Consumer:
    '''
    Kafka comsumer interface for consuming messages from a single topic.
    '''

    def __init__(self, server: str, topic: str):
        self.server = server
        self.topic = topic
        print (self.topic)

        try:
            self.consumer = KafkaConsumer(
                self.topic,
                auto_offset_reset="latest",
                bootstrap_servers=self.server,
                client_id="demo-client-1",
                group_id="demo-group",
                security_protocol="SSL",
                ssl_cafile="auth/ca.pem",
                ssl_certfile="auth/service.cert",
                ssl_keyfile="auth/service.key",
            )
        except Exception as e:
            print(f'Error connecting to Kafka broker: {e}')
            raise e

        # Make initial call to poll which will just assign partitions for our
        # consumer without actually returning anything
        self.consumer.poll(timeout_ms=1)

    def consume(self) -> List[ConsumerRecord]:
        '''
        Collect messages available in single poll call and return as a list.
        '''

        messages = []
        raw_msgs = self.consumer.poll(timeout_ms=1000)
        for tp_messages in raw_msgs.values():
            messages.extend(tp_messages)

        # Commit offsets so we won't get the same messages again
        self.consumer.commit()

        return messages
