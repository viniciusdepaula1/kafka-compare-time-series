from confluent_kafka import Producer, Consumer, KafkaException
import json
import numpy as np
import math
from queue import Queue, Empty
from flask_socketio import SocketIO, emit
from flask import copy_current_request_context
import socketio

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


def balanceamento(num_series, num_maquinas):
    s = np.linspace(1, num_series, num_series)
    #print(s)
    #print(len(s))
    results = []

    num_series_por_maquina = math.ceil(num_series / num_maquinas)
    #print(num_series_por_maquina)

    for m in range(num_maquinas):
        deletar_do_inicio = True
        series = []
        for i in range(num_series_por_maquina):
            if(len(s) > 0):
                if(deletar_do_inicio):
                    series.append(s[0])
                    s = np.delete(s, 0)
                else:
                    series.append(s[-1])
                    s = np.delete(s, -1)
                deletar_do_inicio = not deletar_do_inicio
        #print('máquina ', m+1, ': ', series)
        results.append(series)

    return results


def consumer_fun(consumer, user_event, queue):
    print('listening')
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
                #user_code = json_value['user_code']
                #results = json_value['results']

                #print(results)
                #print(user_code)

                queue.put(json_value)

                print('lancei')
                
                user_event.set()

    except KeyboardInterrupt:
        print("Detected Keyboard Interrupt. Cancelling.")
        pass

    finally:
        consumer.close()


#matrix_size
def user_wait_result(queue, user_event, clients_hashmap, limiter_connection, number_of_workers, flask_socketio):
    print('on')
    
    while True:
            try:
                user_event.wait(timeout=None)
                comparation_results = queue.get()
            except Empty:
                print("Queue 'out_q' is empty")
            else:
                print('to no while true')
                user_code = comparation_results['user_code']
                results = comparation_results['results']

                print('é o results')
                print(results)      
                print('é o usercode')   
                print(clients_hashmap[user_code])
                print('é o limiter_connection')
                print(limiter_connection[user_code])

                flask_socketio.emit('message', 
                    {'results': results, 'sid': clients_hashmap[user_code]}, 
                    room=clients_hashmap[user_code])

                limiter_connection[user_code] += 1
                if(limiter_connection[user_code] == number_of_workers):
                    flask_socketio.emit('disconnect', room=clients_hashmap[user_code])
            