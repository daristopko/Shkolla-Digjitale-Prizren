"""
NumPy Basics - Intro
NumPy është një bibliotekë e fuqishme për llogaritje numerike në Python. 
Ajo ofron një strukturë të dhënash të quajtur "array" 
që është më efikase dhe më e shpejtë se listat e zakonshme të Python-it 
për operacione matematikore dhe shkencore.
"""

import numpy as np

# Version
print("NumPy Version:", np.__version__)

# List vs Array
numrat_list = [10, 20, 30, 40]
print("List + List:", numrat_list + numrat_list)

numrat_array = np.array([10, 20, 30, 40])
print("Array + Array:", numrat_array + numrat_array)