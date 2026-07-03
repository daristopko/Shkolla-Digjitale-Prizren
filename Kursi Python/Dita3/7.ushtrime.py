# =========================================
# USHTRIME – PYTHON (DITA 4)
# =========================================
# =====================================================
# 1. GUESSING GAME
# =====================================================

# Kompjuteri ka një numër sekret
# Përdoruesi duhet ta gjejë numrin

sekreti = 7

while True:

    numri = int(input("Gjeje numrin (1-10): "))

    if numri == sekreti:
        print("🎉 E gjete numrin!")
        break

    else:
        print("❌ Gabim! Provo përsëri.")

# =====================================================
# 2. PATTERN PRINTING
# =====================================================

# Printimi i yjeve me nested loop

for i in range(1, 6):

    for j in range(i):
        print("*", end="") # printon yje në të njëjtin rresht end = "" nuk lejon kalimin në rresht të ri

    print()

# OUTPUT:
#
# *
# **
# ***
# ****
# *****

# =====================================================
# 3. AVERAGE FUNCTION
# =====================================================

# Funksion që llogarit mesataren

def average(a, b, c):

    return (a + b + c) / 3


# marrim rezultatin
rezultati = average(10, 20, 30)

print("Mesatarja është:", rezultati)