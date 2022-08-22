from numpy import broadcast
import requests
import socketio
import uuid
import numpy as np
import os
import sklearn.preprocessing

def read(path):
		"""
		Parameters:
		-----------
			path: data location 
		Returns:
		--------
			The data in matrix form. There are 240 matrices total. 
			Number of columns and rows: 39 and 45.
		"""
		files = os.listdir(path)
		data = []
		for i in files:
			data.append(np.genfromtxt(path+i,skip_header=6))
		return(data)
    
def timeSeriesGen(data):
		"""
		Parameters:
		-----------
			data: Data returned from read() function
		Returns:
		--------
			ts: A set of time series. For example: the time series ts[0] is formed by the value A[0,0] from all matrices.
		"""
		ts = {}
		ts_indexes = {}
		for row in range(len(data[0][:,0])):
			for col in range(len(data[0][0,:])):
				aux = []
				for idx in range(len(data)):
					aux.append(data[idx][row,col])
				ts[col + (len(data[0][0,:])*row)] = aux
				ts_indexes[col + (len(data[0][0,:])*row)] = [row,col]
		return(ts,ts_indexes)

def normalize(x):
    return round(((x - 0) / (103) - (0)),4)     #max value = 103 [716]

def normalize_series(serie):
    vector = []
    for x in serie:
        vector.append(normalize(x))
    return(vector)

data = read('./Data - ESRI/')
series = timeSeriesGen(data)
print(len(series[0]))
for x in range(len(series[0])):
    series[0][x] = normalize_series(series[0][x])

user_code = str(uuid.uuid1())
xd = []
for x in range(40):
    xd.append(series[0][x])

url = 'http://127.0.0.1:5000'
sio = socketio.Client()
sio.connect(url)

splits = np.array_split(xd, 20)
print("From splits \n\n\n\n")
#print(splits)
position = 1

for x in splits:
    test0 = {
        'user_code': user_code, 
        'time_series': x.tolist(),
        'converter_alg': 3,
        'comparator_alg': 3,
        'len_time_series': len(xd),
        'position': position
    }
    position +=1
    sio.emit('message', test0)

test1 = {
    'user_code': user_code, 
    'time_series': [
        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1], 
        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1],
        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1],
        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1],
        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1],
        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1],
        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1],
        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1],
    ],
    'converter_alg': 3,
    'comparator_alg': 2,
}

test2 = {
    'user_code': user_code, 
    'time_series': [
        [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1], 
        [0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1],
        [0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2],
        [0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1],
        [0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2],
        [0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1],
        [0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2],
        [0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1,0,0.1],
    ],
    'converter_alg': 2,
    'comparator_alg': 2,
}

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

#sio.emit('message', test0)
#sio.wait()



