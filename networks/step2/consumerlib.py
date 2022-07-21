from confluent_kafka import Producer, Consumer, KafkaException
import json
import numpy as np
import math
from converter_algs import conv_to_VG, conv_to_DCSD, conv_to_DCTIF
from model import TimeSeries, TimeSeriesSchema, send_receive_network_Schema
from threading import Thread
from producerlib import *
from marshmallow import exceptions

def consumer_fun(consumer, producer, my_position):
    try:
        while True:
            msg = consumer.poll(0.1)
            if not msg:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                record_value = msg.value()
                json_value = json.loads(record_value)
                print(json_value)

                user_code = json_value['user_code']
                time_series = json_value['time_series']
                work_order = json_value['work_order']
                converter_alg = json_value['converter_alg']
                comparator_alg = json_value['comparator_alg']
                len_time_series = json_value['len_time_series']

                validade_time_series = TimeSeriesSchema().load(
		            {'user_code': user_code, 'time_series': time_series, 'work_order': work_order, 
                    'converter_alg': converter_alg, 'comparator_alg': comparator_alg, 'len_time_series': len_time_series})
                
                consume_series = Thread(target=exec_work, args=(validade_time_series, producer, my_position))
                consume_series.start()

    except KeyboardInterrupt:
        print("Detected Keyboard Interrupt. Cancelling.")
        pass

    finally:
        consumer.close()

def select_alg(alg_number):
    if alg_number == 1:
        return conv_to_VG
    elif alg_number == 2:
        return conv_to_DCSD
    elif alg_number == 3:
        return conv_to_DCTIF

def exec_work(data, producer, my_position):
    print('From work')
    
    alg = select_alg(data.get('converter_alg'))
    comparator_alg = data.get('comparator_alg')
    len_time_series = data.get('len_time_series')
    time_series = np.array(data.get('time_series'))
    data_work_order = data.get('work_order')
    user_code = data.get('user_code')

    thread_list = []
    aux_results = {}

    count = 0
    
    for n in data_work_order[my_position-1]:
        thread_list.append(Thread(target=calc_alg, args=(time_series[int(n-1)], alg, int(n-1), aux_results)))
        thread_list[count].start()
        count+=1

    for n in thread_list:
        n.join()

    json_obj = { 'user_code': user_code, 'results': aux_results, 
        'worker_order': data_work_order, 'comparator_alg': comparator_alg, 'len_time_series': len_time_series}

    prod(producer, 'send_receive_networks', 0, json_obj, user_code)
    producer.flush()

def calc_alg(x, alg, count, list):
    r = alg(x)
    to_send_receive_networks = send_receive_network_Schema().load({
                "network": r})
    list[count] = to_send_receive_networks
    print('CLAUCLO')
    print(count)
    print(list)