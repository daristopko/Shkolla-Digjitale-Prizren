# PYTHON BASICS (CASTING + STRING METHODS + ARITHMETIC + COMPARISON + LOGICAL OPERATORS + LISTS + CHALLENGES)

print("=== CASTING ===")

x = "25"
x = int(x)
print(x, type(x))

num = 10
print(float(num))

v = 7.9
print(int(v))

n = 100
n = str(n)

print(n)
print(type(n))



print("\n=== STRING METHODS ===")

text = "python advanced"

print(text.upper())
print(text.lower())
print(text.capitalize())
print(text.title())
print(len(text))



print("\n=== ARITHMETIC OPERATORS ===")

a = 10
b = 3

print("Mbledhja:", a + b)
print("Zbritja:", a - b)
print("Shumzimi:", a * b)
print("Pjestimi:", a / b)
print("Mbetja:", a % b)# mbetja e pjesëtimit
print("Fuqia:", a ** b)# fuqi (10^3)
print("Pjestim i plote:", a // b) # pjestim pa presje dhjetore






print("\n=== COMPARISON OPERATORS ===")

x = 20
y = 20

print("x == y:", x == y)
print("x != y:", x != y)
print("x > y:", x > y)
print("x < y:", x < y)
print("x >= y:", x >= y)
print("x <= y:", x <= y)





print("\n=== LOGICAL OPERATORS ===")

# Shembuj me numra (True / False)

x = 10
y = 20
z = 5

print("x > 5 and y > 15:", x > 5 and y > 15)   # True and True -> True
print("x > 15 or z < 10:", x > 15 or z < 10)   # False or True -> True
print("not (x > y):", not (x > y))              # not False -> True



print("\n=== LISTS ===")
# Lista është një koleksion i elementeve të renditur

my_list = [10, 20, 30]
print("Lista fillestare:", my_list)
# aksesojmë elementin e parë me indeks 0
print("Elementi i parë:", my_list[0])

my_list.append(40)
print("Pas append:", my_list)

my_list.remove(20)
print("Pas remove:", my_list)

print("Gjatësia:", len(my_list))
# len tregon sa elemente ka lista


#Tuples are used to store multiple items in a single variable.
#Tuple is one of 4 built-in data types in Python used to store collections of data, the other 3 are List, Set, and Dictionary, all with different qualities and usage.

text = ('Shkolla', 'Digjitale', 'Prizren')
print(text)

print(len(text))

name = ('Arianit', 'Tershnjaku', 28, True)
print(type(name))

print(name[1])

if 'Arianit' in name:
    print("Arianit")
    
x = list(name)
x.append(80)

name = tuple(x)
print(name)

#Sets are used to store multiple items in a single variable.
#Set is one of 4 built-in data types in Python used to store collections of data, the other 3 are List, Tuple, and Dictionary, all with different qualities and usage.

x = {10, 20, 30}
print(x)

print(len(x))
 
name = {'Arianit', 'Tershnjaku', 28, True}
print(type(name))

text = {"Shkolla", "Digjitale", "Prizren"}
print(text)

for i in text:
    print(i)
    
print("Prizren" in text)

text.add("Prishtine")
print(text)

#text.update()

text.remove("Prishtine")
print(text)


print("")
#challenges
#1.Ushtrim — Calculator i thjeshte

numri1 = input("Shkruaj numrin 1: ")
numri1 = float(numri1)
numri2 = float(input("Shkruaj numrin 2: "))

print("Shuma:", numri1 + numri2)
print("Zbritja:", numri1 - numri2)
print("Shumzimi:", numri1 * numri2)
print("Pjestimi:", numri1 / numri2)

#2.Ushtrim — String Formatting
print("")
emri = input("Emri: ")
mosha = int(input("Mosha: "))
qyteti = input("Qyteti: ")

print(f"Pershendetje {emri}, ti je {mosha} vjec dhe jeton ne {qyteti}.")

print("")
#3. Ushtrim — Number Comparison
a = int(input("Numri 1: "))
b = int(input("Numri 2: "))

print("A eshte a > b:", a > b)
print("A eshte a < b:", a < b)
print("A jane te barabarte:", a == b)