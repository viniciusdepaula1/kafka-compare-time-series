from numpy import broadcast
import requests
import socketio
import uuid

user_code = str(uuid.uuid1())

url = 'http://127.0.0.1:5000'
sio = socketio.Client()
sio.connect(url)

test1 = {
    'user_code': user_code, 
    'time_series': [
        [1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1], 
        [1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1],
        [1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1],
        [1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1],
        [1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1],
        [1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1],
        [1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1],
        [1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1],
    ],
    'traditional_alg': 2,
}

test2 = {
    'user_code': user_code, 
    'time_series': [
        [1,2,3,4,5,6,7,8,9,8,7,6,5,4,3,2,1], 
        [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
        [5,5,5,5,5,5,5,5,2,2,2,2,2,2,2,2,2],
        [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
        [5,5,5,5,5,5,5,5,2,2,2,2,2,2,2,2,2],
        [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
        [5,5,5,5,5,5,5,5,2,2,2,2,2,2,2,2,2],
        [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
    ],
    'traditional_alg': 3,
}

sio.emit('message', test1)

@sio.on('response')
def response(data):
    print(data)  # {'from': 'server'}
    sio.disconnect()
    exit(0)

@sio.on('message')
def message(data):
    print(data)

@sio.on('connect')
def connect():
    sio.emit('connected')

@sio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    sio.disconnect()


