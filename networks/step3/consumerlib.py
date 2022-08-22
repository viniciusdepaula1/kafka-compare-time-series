from confluent_kafka import Producer, Consumer, KafkaException
import json
from httplib2 import ProxiesUnavailableError
import numpy as np
import math
from compare_algs import portrait_comparator, gcd11_comparator, netlsd_comparator
from model import monitorSchema
from threading import Thread
from producerlib import *
from marshmallow import exceptions

def consumer_fun(consumer, producer, networks_hashmap, my_position, clients_hashmap):
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
                results = json_value['results']
                work_order = json_value['worker_order']
                comparator_alg = json_value['comparator_alg']
                len_time_series = json_value['len_time_series']

                json_obj = {'user_code': user_code, 'work_order': work_order, 
                    'comparator_alg': comparator_alg}
                
                if user_code in networks_hashmap:
                    for key, value in results.items():
                        networks_hashmap[user_code][str(key)] = value
                else:
                    networks_hashmap[user_code] = results

                if(len_time_series == len(networks_hashmap[user_code])):
                    consume_series = Thread(target=exec_work, args=(json_obj, networks_hashmap[user_code], producer, my_position))
                    consume_series.start()

    except KeyboardInterrupt:
        print("Detected Keyboard Interrupt. Cancelling.")
        pass

    finally:
        consumer.close()

def select_alg(alg_number):
    if alg_number == 1:
        return portrait_comparator
    elif alg_number == 2:
        return gcd11_comparator
    elif alg_number == 3:
        return netlsd_comparator

def exec_work(data, networks_hashmap, producer, my_position):
    print('From work')

    alg = select_alg(data.get('comparator_alg'))
    len_series = len(networks_hashmap)
    data_work_order = data.get('work_order')
    user_code = data.get('user_code')
    
    thread_list = []
    aux_results = []

    count = 0
    
    if(data.get('comparator_alg') != 2):
        for n in data_work_order[my_position-1]:
            for m in range(int(n), len_series):
                thread_list.append(Thread(target=calc_alg, args=(networks_hashmap[str(int(n)-1)]['network'],  
                    networks_hashmap[str(m)]['network'], n, m, alg, aux_results)))
                thread_list[count].start()
                count+=1
    else:
        for n in data_work_order[my_position-1]:
            for m in range(int(n), len_series):
                calc_alg(networks_hashmap[str(int(n)-1)]['network'],  
                    networks_hashmap[str(m)]['network'], n, m, alg, aux_results)
                count+=1


    for n in thread_list:
        n.join()

    json_obj = { 'user_code': user_code, 'results': aux_results}

    prod(producer, 'monitor', 0, json_obj, user_code)
    producer.flush()

def calc_alg(x, y, n, m, alg, list):
    r = alg(x, y)
    to_monitor = monitorSchema().load({
                "line": int(n)-1, "column": m, "value": r})
    list.append(to_monitor)