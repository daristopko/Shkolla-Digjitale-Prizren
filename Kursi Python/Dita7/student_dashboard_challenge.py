import matplotlib.pyplot as plt
import numpy as np

# CHALLENGE I LEHTE: Notat e Studenteve
#
# Qellimi:
# Krijo nje grafik te thjeshte qe tregon noten mesatare te secilit student.
#
# Detyrat:
# 1. Krijo nje figure te re.
# 2. Krijo nje bar chart per notat mesatare.
# 3. Shto title dhe labels.
# 4. Shfaq grafikun.

students = np.array(["Arta", "Dion", "Elira", "Beni", "Lina"])
average_grades = np.array([8.7, 7.5, 9.2, 6.8, 8.1])

plt.figure()#figure() krijon një figurë të re për grafikun, duke siguruar që grafiku i mëparshëm të mos ndikojë në këtë grafik të ri.
plt.bar(students, average_grades, color="green")

plt.title("Nota mesatare per student")
plt.xlabel("Studentet")
plt.ylabel("Nota mesatare")
plt.grid(axis="y")

plt.show()
