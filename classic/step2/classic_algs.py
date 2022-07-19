import dtw as DTW
import sklearn.feature_selection._mutual_info as mmmi
from scipy import stats

def calcDTW(x1, x2, plotResult):
        alignment = DTW.dtw(x1, x2, keep_internals=True if plotResult else False);
    
        if(plotResult):
            alignment.plot(type="threeway")
            DTW.dtw(x1, x2, keep_internals=True, 
            step_pattern=DTW.rabinerJuangStepPattern(6, "c"))\
            .plot(type="twoway",offset=-2)

        return alignment.distance

def calcDtwAlignment(serie1, serie2):
    return calcDTW(serie1, serie2, False)

def calcPearson(serie1, serie2):
    r, _ = stats.pearsonr(serie1, serie2)
    return r

def calcMi(serie1, serie2):
    return mmmi._compute_mi_cc(serie1, serie2, 4)   #k=4 || k=6
    