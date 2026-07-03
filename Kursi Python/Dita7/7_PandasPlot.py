"""
PLOTTING ME PANDAS DHE MATPLOTLIB

Plotting (vizualizimi i të dhënave) na ndihmon të shohim dhe analizojmë
më lehtë informacionin që gjendet në një dataset.

Në këtë shembull do të përdorim:
- Line Plot (grafik me vija)
- Scatter Plot (grafik me pika)
- Histogram (shpërndarja e të dhënave)

Për këtë përdorim bibliotekat Pandas dhe Matplotlib.
"""

import pandas as pd
import matplotlib.pyplot as plt

# ==================================================
# Leximi i dataset-it nga skedari CSV
# ==================================================

df = pd.read_csv('C:\\Users\\Kebir\\Desktop\\python_ac\\Dita6\\data.csv')

# ==================================================
# LINE PLOT
# ==================================================

# Krijon një grafik me vija për të gjitha kolonat numerike
df.plot()

# Vendos titullin e grafikut
plt.title("Line Plot - Te gjitha kolonat")

# Shfaq grafikun
plt.show()

# ==================================================
# SCATTER PLOT
# ==================================================

# Krahason Duration me Calories
# Çdo pikë përfaqëson një rresht të dataset-it

df.plot(
    kind='scatter',#kind='scatter' tregon se do të krijojmë një grafik me pika
    x='Duration',
    y='Calories'
)

plt.title("Duration vs Calories")
plt.show()

# ==================================================
# SCATTER PLOT 2
# ==================================================

# Krahason Duration me Maxpulse

df.plot(
    kind='scatter',
    x='Duration',
    y='Maxpulse'
)

plt.title("Duration vs Maxpulse")
plt.show()

# ==================================================
# HISTOGRAM
# ==================================================

# Histogrami tregon sa herë paraqitet një vlerë
# ose grup vlerash në kolonën Duration

df["Duration"].plot(kind='hist')

plt.title("Histogram i Duration")
plt.xlabel("Duration")
plt.ylabel("Frekuenca")

plt.show()