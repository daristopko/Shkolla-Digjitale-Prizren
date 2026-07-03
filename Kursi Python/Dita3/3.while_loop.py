# While loop përdoret kur nuk e dimë saktë sa herë do të përsëritet kodi
# Ai vazhdon derisa kushti të jetë TRUE
x = 1  # fillojmë nga 1

while x <= 5:  # vazhdon derisa x të jetë më i vogël ose i barabartë me 5
    print("Vlera e x është:", x)  # shfaq vlerën aktuale
    x = x + 1  # rrit x për 1 (shumë e rëndësishme)

num = 0

print("-------")

while num < 5:
    print("Numri është:", num)
    num += 1  # mënyrë e shkurtër për num = num + 1

print("-------")

password = "1234"
user_input = ""

while user_input != password:
    user_input = input("Shkruaj passwordin: ")

print("Qasja u lejua!")


password = "1234"
attempts = 0

while attempts < 3:
    user_input = input("Shkruaj passwordin: ")

    if user_input == password:
        print("Qasja u lejua!")
        break
    else:
        print("Gabim passwordi!")
    
    attempts += 1

if attempts == 3:
    print("U bllokua llogaria pas 3 tentimeve!")


# =====================
# SHEMBULL 4 - INFINITE LOOP (MOS E HARRO)
# =====================

# KUJDES: Ky loop nuk ndalet kurrë nëse nuk ndalet manualisht

# while True:
#     print("Ky është infinite loop")


# =====================
# SHPJEGIM I SHKURTËR
# =====================

# while = përsërit derisa kushti është TRUE
# nëse kushti bëhet FALSE → loop ndalet
# nëse nuk e ndryshon vlerën → loop nuk ndalet kurrë
