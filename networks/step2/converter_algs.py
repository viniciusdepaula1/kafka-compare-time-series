from DCSD import *
from DCTIF import *
from VG import *

def conv_to_VG(time_serie):
    vg = VG()
    graph = vg.gen_network(time_serie)
    return graph

def conv_to_DCSD(time_serie):
    dcsd = DCSD()
    graph = dcsd.gen_network(time_serie)
    return graph

def conv_to_DCTIF(time_serie):
    dctif = DCTIF()
    graph = dctif.gen_network(time_serie)
    return graph    