import sys
from flask import Flask, jsonify, request
from confluent_kafka import Producer, Consumer, TopicPartition
from model import TimeSeries, TimeSeriesSchema
import json
import uuid
import ccloud_lib
from consumerlib import *
import numpy as np
import math
from queue import Queue, Empty
from threading import Thread, Event

#app = Flask(__name__)
config_file = '../python.config'  # kafka config file
my_position = int(sys.argv[1])

print('position: ', my_position)
topic_to_send = 'monitor'
topic_to_receive = 'send_receive_networks'

#producer instance
conf = ccloud_lib.read_ccloud_config(config_file)
producer_conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
producer = Producer(producer_conf)
ccloud_lib.create_topic(conf, topic_to_send)

#consumer instance
consumer_conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
consumer_conf['group.id'] = 'group_1'           
consumer_conf['auto.offset.reset'] = 'earliest'
consumer = Consumer(consumer_conf)
consumer.assign([TopicPartition(topic_to_receive, 0)])

networks_hashmap = {}

wait_work = Thread(target=consumer_fun, args=(consumer, producer, networks_hashmap, my_position))
wait_work.start()


