# Nested loop do të thotë: një loop brenda një loop tjetër
# Përdoret kur kemi kombinime ose tabela (rreshta dhe kolona)

for i in range(3):
    # loop i jashtëm
    for j in range(2):
        # loop i brendshëm
        print("i:", i, "j:", j)

print("")
# =====================
# SHEMBULL 2 - NUMËRIM ME KOMBINIME
# =====================

#cdo her nuk e merr numrin e fundit te range, pra 4 nuk e merr
for a in range(1, 4):
    for b in range(1, 3):
        print("A:", a, "B:", b)


print("")
# =====================
# SHEMBULL 3 - TABELË SHUMËZIMI
# =====================

for i in range(1, 6):
    for j in range(1, 6):
        print(i, "x", j, "=", i * j)
    print("-----------------")


print("")
# =====================
# SHEMBULL 4 - MODELI ME YJE (*)
# =====================

for i in range(1, 6):
    for j in range(i):
        print("*", end="")  # end-> printon yjet në të njëjtin rresht
    print()  # kalon në rresht të ri

print("")

# =====================
# SHPJEGIM I THJESHTË
# =====================

# Loop i jashtëm = kontrollon rreshtat
# Loop i brendshëm = kontrollon kolonat
# Nested loop = kombinime ose struktura si tabela
