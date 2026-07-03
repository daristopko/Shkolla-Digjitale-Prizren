import matplotlib.pyplot as plt
import numpy as np

# Matplotlib Markers
ypoints = np.array([3, 8, 1, 10])#Krijon një array me numra të caktuar që do të përdoren për të krijuar grafikun me vija.

plt.plot(ypoints, marker = 'o')#marker = 'o' tregon se do të përdorim një marker në formën e një rrethi për secilën pikë në grafikun me vija.
plt.show()

ypoints = np.array([3, 8, 1, 10])

plt.plot(ypoints, 'o:r')#' o:r' është një shkurtesë që kombinon tre argumente: 'o' për markerin në formën e një rrethi, ':' për linjën e praruar dhe 'r' për ngjyrën e kuqe.
plt.show()

# Marker size
ypoints = np.array([3, 8, 1, 10])

plt.plot(ypoints, marker = 'o', ms = 20)#ms = 20 vendos madhësinë e markerit në 20.
plt.show()

# Marker Color
ypoints = np.array([3, 8, 1, 10])

plt.plot(ypoints, marker = 'o', ms = 20, mec = 'r')#mec = 'r' vendos ngjyrën e markerit në të kuqe.
plt.show()

ypoints = np.array([3, 8, 1, 10])

plt.plot(ypoints, marker = 'o', ms = 20, mfc = '#00ff00')#mfc = '#00ff00' vendos ngjyrën e brendshme të markerit në një nuancë të gjelbër.
plt.show()