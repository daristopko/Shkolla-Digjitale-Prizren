"""
Çka është math?

math është modul në Python që përdoret për:
- kalkulime matematikore
- rrënjë katrore
- fuqi
- numra random
- PI
- rounding
"""
import math

#Rrënja Katrorë — sqrt()
print("\n===== 1. PYTHON -> Rrenja katrore =====")
numri = 25

print(math.sqrt(numri))

print("\n===== 2. PYTHON -> Fuqia =====")
#Fuqia — pow()
print(math.pow(2, 3))  # 2 në fuqinë 3

print("\n===== 3. PYTHON -> Numra random =====")
import random
#Numra random
print(random.random())  # numër random mes 0 dhe 1 nuk e përfshin 1
print(random.randint(1, 10))  # numër random mes 1 dhe 10 

print("\n===== 4. PYTHON -> PI =====")
#vlera e PI
print(math.pi)

print("\n===== 5. PYTHON -> Rounding =====")
#rounding
print(round(3.2))
print(round(3.5))
print(round(3.8))

print("\n===== 6. PYTHON -> Rounding UP(ceil) =====")
#Rounding UP — ceil()
print(math.ceil(3.2))  # 4

print("\n===== 7. PYTHON -> Rounding DOWN(floor) =====")
#Rounding DOWN — floor()
print(math.floor(3.8))  # 3

print("\n===== 8. PYTHON -> Absolute value =====")
#Absolute value — fabs()
print(math.fabs(-5))  # 5.0

print("\n===== 9. PYTHON -> Min and Max =====")
#minimum dhe maksimum
x = min(5, 10, 25)
y = max(5, 10, 25)
 
print(x)
print(y)