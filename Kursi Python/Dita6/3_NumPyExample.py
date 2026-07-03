"""
Numpy eshte nje library e fuqishme per te punuar me array dhe matrica ne Python.
Ajo ofron funksione te avancuara per te manipuluar dhe analizuar te dhenat numerike, duke perfshire:
- Krijimi i array dhe matrica me vlera te ndryshme
- Operacione matematikore dhe statistike mbi array dhe matrica
- Manipulimi i dimensioneve te array dhe matrica
Numpy eshte shume i dobishem per te punuar me te dhenat numerike ne fushat e Data Science, Machine Learning, dhe Analizes se te Dhenave.
"""

import numpy as np

# Krijimi i një matrice 2x3 të zbrazët
matrice = np.zeros((2, 3))
print(matrice)

# Krijimi i një matrice 2x3 me vlera të rastësishme në mes 0 dhe 1
matrice_rastësishme = np.random.rand(2, 3)
print(matrice_rastësishme)

# Krijimi i dy matricave të shkallës 2x3
matrice1 = np.array([[1, 2, 3], [4, 5, 6]])
matrice2 = np.array([[7, 8, 9], [10, 11, 12]])

# Mbledhja e dy matricave
mbledhja = matrice1 + matrice2
#mbledhja = matrice1[0] + matrice2[1]
print(mbledhja)

# Shumëzimi i një matrice me një numër
shumëzimi = matrice1 * 2
print(shumëzimi)

# Krijimi i një matrice 2x2
matrice = np.array([[1, 2], [3, 4]])

# Kalkulimi i logaritmit natyral për secilën vlerë në matricë
log_matrice = np.log(matrice)
print(log_matrice)

# Kalkulimi i sinusit për secilën vlerë në matricë
sinus_matrice = np.sin(matrice)
print(sinus_matrice)