# FOR LOOP - përdoret për me përsërit diçka disa herë.
#i-> eshte variabel qe merr vlera nje nga nje.
#range(start, stop, step)kontrollon sa here perseritet kodi
#range gjithmone fillon nga 0
#range nuk e perfshin numrin e fundit

for i in range(5):
    print("Numri eshte:", i)
print('')

for i in range(1, 6):
    print(i)
print('')

for i in range(0, 10, 2):
    print(i)
print('')

# for loop me liste
emrat = ["Kebir", "Arianit", "Dafina"]

for emri in emrat:
    print("Emri:", emri)