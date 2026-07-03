# Matplotlib Bars eshte një mënyrë për të vizualizuar të dhënat në formën e kolonave horizontale ose vertikale. 
# Kjo është veçanërisht e dobishme për të krahasuar vlera të ndryshme në kategori të ndryshme.
import matplotlib.pyplot as plt
import numpy as np

# Horizontal
x = np.array(["A", "B", "C", "D"])
y = np.array([30, 40, 10, 20])

plt.barh(x, y) # barh() krijon një grafik me kolonat horizontale. 
#x janë kategoritë dhe y janë vlerat për secilën kategori.
plt.show()

plt.bar(x, y, color = "red") # bar() krijon një grafik me kolonat vertikale.
plt.show()