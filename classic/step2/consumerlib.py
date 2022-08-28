from confluent_kafka import KafkaException
import json
import numpy as np
from classic_algs import calcDtwAlignment, calcMi, calcPearson
from model import TimeSeriesSchema, monitorSchema
from threading import Thread
from producerlib import *
import time
import csv

def consumer_fun(consumer, producer, my_position, clients_hashmap):
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

                user_code = json_value['user_code']
                time_series = json_value['time_series']
                work_order = json_value['work_order']
                traditional_alg = json_value['traditional_alg']
                len_time_series = json_value["len_time_series"]
                position = json_value["position"]

                validade_time_series = TimeSeriesSchema().load(
		            {'user_code': user_code, 'time_series': time_series, 'work_order': work_order, 
                        'traditional_alg': traditional_alg, 'len_time_series': len_time_series, 'position': position})
                
                if(user_code in clients_hashmap):
                    clients_hashmap[user_code][position] = time_series
                    if(len(clients_hashmap[user_code]) == 40):
                        vector_final = []
                        for i in range(1, 41):
                            vector_final.extend(clients_hashmap[user_code][i])
                        
                        validade_time_series = TimeSeriesSchema().load(
		                    {'user_code': user_code, 'time_series': vector_final, 'work_order': work_order, 
                            'traditional_alg': traditional_alg, 'len_time_series': len_time_series, 'position': position})

                        consume_series = Thread(target=exec_work, args=(validade_time_series, producer, my_position))
                        consume_series.start()
                else:
                    if(len(time_series) == len_time_series):
                        print('chegay')
                        consume_series = Thread(target=exec_work, args=(validade_time_series, producer, my_position))
                        consume_series.start()
                    else:
                        clients_hashmap[user_code] = {}
                        clients_hashmap[user_code][position] = time_series
            
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
    ts = time.time()

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

    splits = np.array_split(aux_results, 80)
    print("From splits \n\n\n\n")
    #print(splits)
    for x in splits:
        json_array = x.tolist()
        json_obj = { 'user_code': user_code, 'results': json_array}
        prod(producer, 'monitor', 0, json_obj, user_code)

    ts2 = time.time()
    ts3 = ts2 - ts
    header_csv = ['init, finish, time_total']
    data_csv=[ts, ts2, ts3]
    
    with open('classic_step2_2workers_alg1.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header_csv)

        # write the data
        writer.writerow(data_csv)

    producer.flush()

def calc_alg(x, y, n, m, alg, list):
    r = alg(x, y)
    to_monitor = monitorSchema().load({
                "line": int(n)-1, "column": m, "value": r})
    list.append(to_monitor)