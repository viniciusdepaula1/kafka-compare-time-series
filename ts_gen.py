import imp
import os
import numpy as np
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