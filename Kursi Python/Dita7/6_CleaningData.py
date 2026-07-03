"""
DATA CLEANING ME PANDAS

Data Cleaning (Pastrimi i të Dhënave) është procesi i rregullimit të
të dhënave të pasakta ose jo të plota në një dataset.

Problemet më të zakonshme janë:
- Qeliza të zbrazëta (Empty Cells)
- Format i gabuar i të dhënave (Wrong Format)
- Të dhëna të gabuara (Wrong Data)
- Të dhëna të dyfishuara (Duplicates)

Pandas na ndihmon t'i gjejmë dhe t'i rregullojmë këto probleme.
"""

import pandas as pd

# Leximi i dataset-it nga skedari CSV
df = pd.read_csv('C:\\Users\\Kebir\\Desktop\\python_ac\\Dita6\\data.csv')

# ==================================================
# EMPTY CELLS (Qelizat e zbrazëta)
# ==================================================

# dropna() heq të gjitha rreshtat që kanë vlera bosh (NaN)
new_df = df.dropna()

print("Dataset pa rreshtat bosh:")
print(new_df.to_string())

# ==================================================
# Zëvendësimi i vlerave bosh
# ==================================================

# Mbush të gjitha vlerat bosh me numrin 130
df.fillna(130, inplace=True)

# Gjen mesataren e kolonës "Calories" .mean() llogarit mesataren e kolonës
x = df["Calories"].mean()

# Mbush vlerat bosh në kolonën "Calories" me mesataren
df["Calories"].fillna(x, inplace=True) # Nëse ka vlera bosh në kolonën "Calories", ato do të zëvendësohen me mesataren e kolonës.

# Mund të përdorim edhe:
# median() -> medianën
# mode()[0] -> modën

# ==================================================
# WRONG FORMAT (Format i gabuar)
# ==================================================

# Konverton kolonën Date në format datash
# Nëse ka data të gabuara do të bëhen NaT (Not a Time)

# df['Date'] = pd.to_datetime(df['Date'])

# Heq rreshtat që kanë datë të pavlefshme
# df.dropna(subset=['Date'], inplace=True)

# print(df.to_string())

# ==================================================
# WRONG DATA (Të dhëna të gabuara)
# ==================================================

# Ndryshon vlerën në rreshtin 10 të kolonës Duration
df.loc[10, 'Duration'] = 60

# Kontrollon kolonën Duration
# Nëse vlera është më e madhe se 60,
# zëvendësohet me 60

for x in df.index:#df.index kthen të gjithë indeksat (rreshtat) e DataFrame-it.
    if df.loc[x, "Duration"] > 60:
        df.loc[x, "Duration"] = 60


print("\nDataset pas korrigjimit të të dhënave:")
print(df.to_string())#e shfaq krejt tabelën komplet, pa fshehje

# ==================================================
# DUPLICATES (Të dhëna të dyfishuara)
# ==================================================

# Tregon cilët rreshta janë dublikatë
print("\nKontrolli për dublikatë:")
print(df.duplicated().to_string())

# Heq të gjitha dublikatat
df.drop_duplicates(inplace=True)

print("\nDataset pa dublikatat:")
print(df.to_string())

# ==================================================
# DATA CORRELATION
# ==================================================

# corr() llogarit lidhjen mes kolonave numerike
# Rezultati është nga -1 deri në 1

print("\nKorelacioni i të dhënave:")
print(df.corr())
"""
Rregullat kryesore:
Vlera	Kuptimi
1.0	    lidhje perfekte (e njëjta gjë)
afër 1	lidhje e fortë pozitive
afër 0	nuk ka lidhje
afër -1	lidhje negative
"""