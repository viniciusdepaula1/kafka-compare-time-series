import netlsd
from portrait_divergence.portrait_divergence import portrait_divergence
import os
import igraph as ig
import networkx as nx

#networkx
def portrait_comparator(network1, network2):
    grafo1 = ig.Graph.Adjacency(network1, mode='undirected')
    grafo2 = ig.Graph.Adjacency(network2, mode='undirected')
    
    g1_nx = grafo1.to_networkx()
    g2_nx = grafo2.to_networkx()
    
    r = portrait_divergence(network1, network2)

    return r

#ig
def netlsd_comparator(network1, network2):
    grafo1 = ig.Graph.Adjacency(network1, mode='undirected')
    grafo2 = ig.Graph.Adjacency(network2, mode='undirected')
    
    desc1 = netlsd.heat(grafo1)
    desc2 = netlsd.heat(grafo2)

    distance = netlsd.compare(desc1, desc2)

    return distance

#ig
def gcd11_comparator(network1, network2):
    grafo1 = ig.Graph.Adjacency(network1, mode='undirected')
    grafo2 = ig.Graph.Adjacency(network2, mode='undirected')

    toLeda(grafo1, './GCD-11/count/network1.gw')
    toLeda(grafo2, './GCD-11/count/network2.gw')

    os.system("(cd ./GCD-11/count && python count.py network1.gw)")
    os.system("(cd ./GCD-11/count && python count.py network2.gw)")

    os.system("(cd ./GCD-11 && python3 networkComparison.py ./count 'gcd11' 1)")

    r = readResults()  

    return r


def toLeda(network1, file_name):
    network1.write_leda(file_name, names=None, weights=None)

def readResults():
    file = open('./GCD-11/count/gcd11.txt')
    file.readline()
    results = file.readline().split('\t')
    final = results[2].rstrip()
    return float(final)