import matplotlib.pyplot as plt
import numpy as np

# Matplotlib Scatter

# Day one, the age and speed of 13 cars:
x = np.array([5, 7, 8, 7, 2, 17, 2, 9, 4, 11, 12, 9, 6])
y = np.array([99, 86, 87, 88, 111, 86, 103, 87, 94, 78, 77, 85, 86])
plt.figure()#figure() krijon një figurë të re për grafikun e shpërndarjes, duke siguruar që grafiku i mëparshëm të mos ndikojë në këtë grafik të ri.
plt.scatter(x, y)#scatter() krijon një grafik me pika, ku x janë vlerat për boshtin horizontal dhe y janë vlerat për boshtin vertikal. Çdo pikë në grafik përfaqëson një kombinim të vlerave x dhe y.
plt.show()

# Day two, the age and speed of 15 cars:
x = np.array([2, 2, 8, 1, 15, 8, 12, 9, 7, 3, 11, 4, 7, 14, 12])
y = np.array([100, 105, 84, 105, 90, 99, 90, 95, 94, 100, 79, 112, 91, 80, 85])
plt.figure()
plt.scatter(x, y)
plt.show()

# Color
x = np.array([5, 7, 8, 7, 2, 17, 2, 9, 4, 11, 12, 9, 6])
y = np.array([99, 86, 87, 88, 111, 86, 103, 87, 94, 78, 77, 85, 86])
colors = np.array([0, 10, 20, 30, 40, 45, 50, 55, 60, 70, 80, 90, 100])

plt.figure()
plt.scatter(x, y, c=colors, cmap="viridis")#c=colors tregon se do të përdorim vlerat në array-n colors për të përcaktuar ngjyrën e secilës pikë në grafik. 
#cmap="viridis" specifikon që do të përdorim një kolormapë të quajtur "viridis" për të përcaktuar ngjyrat bazuar në vlerat e colors.
plt.colorbar()
plt.show()

# Size
x = np.array([5, 7, 8, 7, 2, 17, 2, 9, 4, 11, 12, 9, 6])
y = np.array([99, 86, 87, 88, 111, 86, 103, 87, 94, 78, 77, 85, 86])
sizes = np.array([20, 50, 100, 200, 500, 1000, 60, 90, 10, 300, 600, 800, 75])#Krijon një array me numra të caktuar që do të përdoren për të përcaktuar madhësinë e secilës pikë në grafik. 
#Vlerat më të mëdha në sizes do të rezultojnë në pika më të mëdha në grafik.

plt.figure()
plt.scatter(x, y, s=sizes)
plt.show()
