import matplotlib.pyplot as plt
import numpy as np

x = np.random.normal(170, 10, 250)#Krijon një array me 250 numra të gjeneruar 
#nga një shpërndarje normale me mesatare 170 dhe devijim standard 10.

plt.hist(x)#hist() krijon një histogram që tregon shpërndarjen e të dhënave në kolonën x.
plt.show() 