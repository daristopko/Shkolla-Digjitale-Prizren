#Python Polymorphism
print("\nPython Polymorphism")

#The word "polymorphism" means "many forms", and in programming it refers to methods/functions/operators with the same name that can be executed on many objects or classes.

#Function Polymorphism
#An example of a Python function that can be used on different objects is the len() function.

#String
x = "Arianit Tershnjaku" 

print(len(x))

#Tuple
text = ("Shkolla", "Digjitale", "Prizren")

print(len(text))

#Dictionary
text = {
    "First Name": "Arianit",
    "Last Name": "Tershnjaku",
    "Age": 28
}

print(len(text))


#Class Polymorphism
print("\n Class Polymorphism")

#Polymorphism is often used in Class methods, where we can have multiple classes with the same method name.

class Car:
  def __init__(self, brand, model):
    self.brand = brand
    self.model = model

  def move(self):
    print("Drive!")

class Boat:
  def __init__(self, brand, model):
    self.brand = brand
    self.model = model

  def move(self):
    print("Sail!")

class Plane:
  def __init__(self, brand, model):
    self.brand = brand
    self.model = model

  def move(self):
    print("Fly!")

car1 = Car("Tesla", "X")       #Create a Car class
boat1 = Boat("Ibiza", "Touring 20") #Create a Boat class
plane1 = Plane("Boeing", "747")


#Create a Plane class
 
for x in (car1, boat1, plane1):
  x.move()



#Inheritance Class Polymorphism
print("\n Inheritance Class Polymorphism")

class Vehicle:
  def __init__(self, brand, model):
    self.brand = brand
    self.model = model

  def move(self):
    print("Move!")

class Car(Vehicle):
  pass

class Boat(Vehicle):
  def move(self):
    print("Sail!")

class Plane(Vehicle):
  def move(self):
    print("Fly!")

car1 = Car("Tesla", "X") #Create a Car object
boat1 = Boat("Ibiza", "Touring 20") #Create a Boat object
plane1 = Plane("Boeing", "747") #Create a Plane object

for x in (car1, boat1, plane1):
  print(x.brand)
  print(x.model)
  x.move()