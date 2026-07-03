"""
Ne kete shembull do te lexojme nje file CSV dhe do te shfaqim te dhenat e tij ne formatin e nje DataFrame.
Ne fillim, ne importojme biblioteken pandas dhe pastaj perdorim funksionin read_csv per te lexuar file CSV dhe per te krijuar nje DataFrame.
Ne fund, ne shfaqim te dhenat e DataFrame dhe informacione te tjera rreth tij.
"""
import pandas as pd
# Read CSV file
df = pd.read_csv('C:\\Users\\ArianitDB\\Desktop\\python ACPz\\Dita6\\data.csv')

print(df)

print(pd.options.display.max_rows)



# Read CSV file
df = pd.read_csv('C:\\Users\\ArianitDB\\Desktop\\python ACPz\\Dita6\\data.csv')

print(df.head())

print(df.tail())

print(df.info()) 