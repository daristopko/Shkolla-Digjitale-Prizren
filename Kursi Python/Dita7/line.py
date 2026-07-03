# Matplotlib Line
import matplotlib.pyplot as plt
import numpy as np

ypoints = np.array([3, 8, 1, 10,2,3,4,5,6,3,2,1,3,5,4,3,2,6,7,8,9,10])#Krijon një array me numra të caktuar që do të përdoren për të krijuar grafikun me vija.

plt.plot(ypoints, linestyle = 'dotted')
plt.show()

ypoints = np.array([3, 8, 1, 10])

plt.plot(ypoints, color = '#ff0000')
plt.show()


ypoints = np.array([3, 8, 1, 10])

plt.plot(ypoints, linewidth = '20.5')
plt.show()

# Multiple Lines
y1 = np.array([3, 8, 1, 10])
y2 = np.array([6, 2, 7, 11])

plt.plot(y1)
plt.plot(y2)

plt.show()