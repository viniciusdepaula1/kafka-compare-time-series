import sys
import ccloud_lib
from confluent_kafka import Producer, Consumer, TopicPartition
from consumerlib import *
from threading import Thread

#app = Flask(__name__)
config_file = '../python.config'  # kafka config file
my_position = int(sys.argv[1])

print('position: ', my_position)
topic_to_send = 'monitor'
topic_to_receive = 'send_receive_time_series'

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

wait_work = Thread(target=consumer_fun, args=(consumer, producer, my_position))
wait_work.start()


