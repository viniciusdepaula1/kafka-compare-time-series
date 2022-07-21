from confluent_kafka import Producer, Consumer
import json
import numpy as np
import math

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: {}".format(err))
    else:
        print("Produced record to topic {} partition [{}] @ offset {}"
              .format(msg.topic(), msg.partition(), msg.offset()))

def prod(producer, topic, partition, value, user_code):
    record_key = user_code
    record_value = json.dumps(value)
    print("Producing record: {}\t{}".format(record_key, record_value))
    producer.produce(topic, key=record_key, value=record_value,
                     on_delivery=acked, partition=partition)
    producer.poll(0)