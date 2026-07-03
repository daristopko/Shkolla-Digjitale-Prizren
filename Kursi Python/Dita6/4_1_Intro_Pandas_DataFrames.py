#pip install pandas
#Pse përdorim Pandas?
"""
Pandas është një bibliotekë e fuqishme për manipulimin dhe analizën e të dhënave në Python. Ajo ofron struktura të dhënash të lehta për t'u përdorur dhe funksione të avancuara për të punuar me të dhëna të ndryshme, duke përfshirë:
DataFrame: Një strukturë e dhënash 2D që mund të përmbajë të dhëna të ndryshme në kolona të ndryshme.
Series: Një strukturë e dhënash 1D që mund të përmbajë të dhëna të një lloji të vetëm.
Pandas është shumë i dobishëm për:
Manipulimin e të dhënave: Pandas ofron funksione të fuqishme për të filtruar, grupuar, dhe transformuar të dhënat.
Analizën e të dhënave: Pandas ofron funksione të avancuara për të analizuar të dhënat, duke përfshirë statistika, agregime, dhe vizualizime.
Pandas është shumë i përdorur në fushat e Data Science, Machine Learning, dhe Analizës së të Dhënave.
"""

import pandas as pd

mydataset = {
  'Programing Language': ["PHP", "SQL", "Python"],
  'years': [3, 7, 2]
}

myvar = pd.DataFrame(mydataset)

print(myvar)


print(pd.__version__)

#Panda Series

a = [1, 7, 2]

myvar = pd.Series(a)

print(myvar)


a = [1, 7, 2]

myvar = pd.Series(a, index = ["x", "y", "z"])

print(myvar)

calories = {"day1": 420, "day2": 380, "day3": 390}

myvar = pd.Series(calories, index = ["day1", "day2", "day3"])

print(myvar)

#DataFrame eshte nje strukture e dhënash 2D që mund të përmbajë të dhëna të ndryshme në kolona të ndryshme. 
# Ajo është shumë e dobishme për manipulimin dhe analizën e të dhënave në Python.
#Krijimi i një DataFrame nga një dictionary
import pandas as pd

data = {
  "calories": [420, 380, 390, 550, 660],
  "duration": [50, 40, 45, 60, 80]
}

#load data into a DataFrame object:
df = pd.DataFrame(data)

print(df) 

# print(df.loc[0])

# print(df.loc[[0, 4]])