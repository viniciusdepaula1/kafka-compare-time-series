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
    print("Producing record: {}".format(record_key))
    producer.produce(topic, key=record_key, value=record_value,
                     on_delivery=acked, partition=partition)
    producer.poll(0)


def balanceamento(num_series, num_maquinas):
    lista_series = list(np.linspace(1, num_series, num_series))
    n_maq = num_maquinas
    #print(lista_series)
    
    maqs = np.empty((n_maq, 0)).tolist()
    #print(maqs)

    cont_maquina = 0
    reverso = False
    while(len(lista_series) > 0):

        #print('mq' + str(cont_maquina) + ' = ', str(lista_series.pop(0)))
        maqs[cont_maquina].append(lista_series.pop(0))

        if(reverso):
            if(cont_maquina == 0 and len(lista_series) > 0):
                #print('mq' + str(cont_maquina) + ' = ', str(lista_series.pop(0)))
                maqs[cont_maquina].append(lista_series.pop(0))
                reverso = not reverso
                cont_maquina += 1
            else:
                cont_maquina -= 1
        else:
            if(cont_maquina == n_maq-1 and len(lista_series) > 0):
                #print('mq' + str(cont_maquina) + ' = ', str(lista_series.pop(0)))
                maqs[cont_maquina].append(lista_series.pop(0))
                reverso = not reverso
                cont_maquina -= 1
            else:
                cont_maquina += 1

    return maqs


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

                queue.put(json_value)
                
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
                user_code = comparation_results['user_code']
                results = comparation_results['results']

                if(user_code in clients_hashmap):
                    print('sending to client')
                    flask_socketio.emit('message', 
                        {'results': results, 'sid': clients_hashmap[user_code]}, 
                        room=clients_hashmap[user_code])

                    limiter_connection[user_code] += 1
                    if(limiter_connection[user_code] >= 160):
                        print('closing connection')
                        flask_socketio.emit('disconnect', room=clients_hashmap[user_code])
                else:
                    print('user not in database')
            