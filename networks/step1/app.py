from ast import arg
from queue import Queue, Empty
from socket import socket
from threading import Thread, Event
from flask import Flask, jsonify, request
from confluent_kafka import Producer, Consumer
from numpy import matrix
from model import TimeSeries, TimeSeriesSchema
import json
import uuid
import ccloud_lib
from producerlib import *
from flask_socketio import SocketIO, emit

app = Flask(__name__)
async_mode = None

clients = []

socketio = SocketIO(app)

config_file = '../python.config'  # kafka config file
number_of_workers = 2
topic_to_send = 'send_receive_time_series'
topic_to_receive = 'monitor'

#producer instance
conf = ccloud_lib.read_ccloud_config(config_file)
producer_conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
producer = Producer(producer_conf)
ccloud_lib.create_topic(conf, topic_to_send)

# consumer instance
consumer_conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
consumer_conf['group.id'] = 'group_1'
consumer_conf['auto.offset.reset'] = 'earliest'
consumer = Consumer(consumer_conf)
consumer.subscribe([topic_to_receive])

clients_hashmap = {}
limiter_connection = {}
user_event = Event()
q = Queue()

monitor_thread = Thread(target=consumer_fun, args=(consumer, user_event, q))
user_thread = Thread(target=user_wait_result, args=(q, user_event, clients_hashmap, limiter_connection, number_of_workers, socketio))

user_thread.start()
monitor_thread.start()

@socketio.on('message')
def message(data):
    user_code = data["user_code"]
    time_series = data["time_series"]
    converter_alg = data["converter_alg"]
    comparator_alg = data["comparator_alg"]
    
    work_order = balanceamento(len(time_series), number_of_workers)

    validade_time_series = TimeSeriesSchema().load(
		{'user_code': user_code, 'time_series': time_series, 'work_order': work_order, 
        'converter_alg': converter_alg, 'comparator_alg': comparator_alg, 'len_time_series': len(time_series)})

    clients_hashmap[user_code] = request.sid
    limiter_connection[user_code] = 0

    prod(producer, topic_to_send, 0, validade_time_series, user_code)
    producer.flush()

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)
