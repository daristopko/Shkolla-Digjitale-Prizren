# Python – Functions

# Function = bllok kodi që përdoret sa herë të duam

# =====================
# FUNCTION PA PARAMETRA
# =====================

# krijimi i funksionit
def pershendetje():
    
    # kodi brenda funksionit
    print("Pershendetje nxenes!")

# thirrja e funksionit
pershendetje()
pershendetje()

# =====================
# FUNCTION TJETËR PA PARAMETRA
# =====================

def info():
    print("Kursi: Python")
    print("Niveli: Fillestar")

info()

# =====================
# FUNCTIONS ME PARAMETERS
# =====================

# parametrat janë vlera që i japim funksionit

def pershendetje_emri(emri):
    print("Pershendetje", emri)

# dërgojmë vlerë te funksioni
pershendetje_emri("Kebir")
pershendetje_emri("Arianit")


# =====================
# FUNCTION ME 2 PARAMETERS
# =====================

def mbledh(a, b):
    print("Shuma është:", a + b)

mbledh(5, 3)
mbledh(10, 20)


# =====================
# RETURN
# =====================

# return përdoret për me kthyer një vlerë

def shumezo(a, b):
    return a * b

# ruajmë rezultatin në variabël
rezultati = shumezo(4, 5)

print("Rezultati është:", rezultati)


# =====================
# NDRYSHIMI print vs return
# =====================

# print vetëm e shfaq vlerën
def test1():
    print(10)# nuk kthen vlerë, vetëm e shfaq

x = test1() # x do të jetë None sepse funksioni nuk kthen vlerë
print(x+2)

# return e kthen vlerën
def test2():
    return 10 # kthen vlerën 10, x do të jetë 10

x = test2()
print(x + 10)