"""
Numpy Arrays Dimensions jane array me dimensione te ndryshme, te cilat mund te jene 0D, 1D, 2D, ose 3D.
0D array eshte nje array me zero dimensione, i cili permban nje vler te vetme.
1D array eshte nje array me nje dimension, i cili eshte nje varg i thjeshte numrash.
2D array eshte nje array me dy dimensione, i cili eshte nje matrice.
3D array eshte nje array me tre dimensione, i cili eshte nje tensor(tensor eshte nje array me tre dimensione).
"""
import numpy as np

# 1D array eshte nje array me nje dimension, i cili eshte nje varg i thjeshte numrash.
arr1 = np.array([1, 2, 3, 4]) 
print("1D:", arr1)

# 0D array eshte nje array me zero dimensione, i cili permban nje vler te vetme.
arr0 = np.array(42)
print("0D:", arr0)

# 2D array eshte nje array me dy dimensione, i cili eshte nje matrice.
arr2 = np.array([
    [1, 2, 3],
    [4, 5, 6]
])
print("2D:\n", arr2)

# 3D array eshte nje array me tre dimensione, i cili eshte nje tensor(tensor eshte nje array me tre dimensione).
arr3 = np.array([
    [
        [1, 2, 3],
        [4, 5, 6]
    ],
    [
        [7, 8, 9],
        [10, 11, 12]
    ]
])
print("3D:\n", arr3)

print("Type:", type(arr1))
