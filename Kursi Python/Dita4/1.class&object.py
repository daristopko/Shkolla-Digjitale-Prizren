#Python Classes and Objects
#Python is an object oriented programming language.
#Almost everything in Python is an object, with its properties and methods.
#A Class is like an object constructor, or a "blueprint" for creating objects. 
  
class klasa:
  x = 10 

print(klasa)

#Object
p1 = klasa()
print(p1.x)
  
print("\nThe __init__() Function")
class Person:
  def __init__(self, name, age):
    self.x = name
    self.y = age

p2 = Person("Arianit", 31)
print(p2.x)
print(p2.y)

p3 = Person("Niti", 28)
print(p3.x)
print(p3.y)

print("\nThe __str__() Function")
class Person:
  def __init__(self, name, age):
    self.x = name
    self.y = age
  
  def __str__(self1):
    return f"{self1.x}({self1.y})"

p1 = Person("Arianit", 28)
print(p1)

p2 = Person("Edin", 20)
print(p2)



print("\nObject Methods")
class Person:
  def __init__(self, name, age):
    self.x = name
    self.y = age

  def fun(self):
    print("Hello my name is " + self.x)

p1 = Person("Arianit", 28)
p1.fun()

print("\nThe self Parameter")
class Person:
  def __init__(mysillyobject, name, age):
    mysillyobject.x = name
    mysillyobject.y = age

  def myfunc(abc):
    print("Hello my name is " + abc.x)

p1 = Person("John", 36)
p1.myfunc()

#ADD
p1.y = 40
print(p1.y)

del p1.y

#print(p1.y)
