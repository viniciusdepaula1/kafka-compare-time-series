from confluent_kafka import KafkaException
import json
import numpy as np
from classic_algs import calcDtwAlignment, calcMi, calcPearson
from model import TimeSeriesSchema, monitorSchema
from threading import Thread
from producerlib import *

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
                traditional_alg = json_value['traditional_alg']

                validade_time_series = TimeSeriesSchema().load(
		            {'user_code': user_code, 'time_series': time_series, 'work_order': work_order, 'traditional_alg': traditional_alg})
                
                consume_series = Thread(target=exec_work, args=(validade_time_series, producer, my_position))
                consume_series.start()

    except KeyboardInterrupt:
        print("Detected Keyboard Interrupt. Cancelling.")
        pass

    finally:
        consumer.close()

def select_alg(alg_number):
    if alg_number == 1:
        return calcDtwAlignment
    elif alg_number == 2:
        return calcMi
    elif alg_number == 3:
        return calcPearson

def exec_work(data, producer, my_position):
    print('From work')
    
    alg = select_alg(data.get('traditional_alg'))
    len_series = len(data.get('time_series'))
    time_series = np.array(data.get('time_series'))
    data_work_order = data.get('work_order')
    user_code = data.get('user_code')

    thread_list = []
    aux_results = []

    count = 0
    
    for n in data_work_order[my_position-1]:
        for m in range(int(n), len_series):
            thread_list.append(Thread(target=calc_alg, args=(time_series[int(n)-1],  time_series[m], n, m, alg, aux_results)))
            thread_list[count].start()
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