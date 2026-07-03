"""
Ne kete shembull do te krijojme nje DataFrame nga nje dictionary dhe do te shfaqim te dhenat e tij.
Ne fillim, ne importojme biblioteken pandas dhe pastaj krijojme nje dictionary me te dhenat qe duam te shfaqim ne DataFrame.
Ne fund, ne krijojme nje DataFrame nga dictionary dhe shfaqim te dhenat e tij.
Ne fund, ne lexojme nje file JSON dhe shfaqim te dhenat e tij ne formatin e nje DataFrame.
"""
import pandas as pd

data = {
  "Duration":{
    "0":60,
    "1":60,
    "2":60,
    "3":45,
    "4":45,
    "5":60
  },
  "Pulse":{
    "0":110,
    "1":117,
    "2":103,
    "3":109,
    "4":117,
    "5":102
  },
  "Maxpulse":{
    "0":130,
    "1":145,
    "2":135,
    "3":175,
    "4":148,
    "5":127
  },
  "Calories":{
    "0":409,
    "1":479,
    "2":340,
    "3":282,
    "4":406,
    "5":300
  }
}

df = pd.DataFrame(data)

print(df) 

print("Data Json")

df = pd.read_json('C:\\Users\\ArianitDB\\Desktop\\python ACPz\\Dita6\\data.json')

print(df.to_string())