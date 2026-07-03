"""
Numpy Indexing and Slicing jane menyra per te aksesuar dhe 
manipuluar elementet e nje array ne baze te pozicionit te tyre.
Indexing eshte menyra per te aksesuar nje element te vecante ne nje array duke
përdorur pozicionin e tij.
Slicing eshte menyra per te aksesuar nje pjese te array duke përdorur
një interval të pozicioneve.
"""
import numpy as np

# Indexing
x = np.array([1, 2, 3, 4])
print(x[1])
print(x[2] + x[3])

# 2D indexing
y = np.array([
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10]
])

print("y[0,1]:", y[0, 1])
print("y[1,2]:", y[1, 2])

# 3D indexing
z = np.array([
    [
        [1, 2, 3],
        [4, 5, 6]
    ],
    [
        [7, 8, 9],
        [10, 11, 12]
    ]
])

print("z[0,1,2]:", z[0, 1, 2])

# Slicing
a = np.array([1, 2, 3, 4, 5, 6, 7])

print(a[0:5])
print(a[2:])
print(a[:4])