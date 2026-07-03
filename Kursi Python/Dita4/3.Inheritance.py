print("Python Inheritancen")
#Inheritance allows us to define a class that inherits all the methods and properties from another class.
#Parent class is the class being inherited from, also called base class.
#Child class is the class that inherits from another class, also called derived class.

#Create a Parent Class 
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

#Use the Person class to create an object, and then execute the printname method:

x = Person("Arianit", "Tershnjaku")
x.printname()


class Student(Person):
  pass


print("Add the __init__() Function")
#Add the __init__() Function

class Student(Person):
  def __init__(self, fname, lname):
    Person.__init__(self, fname, lname)

x = Student("Arianit", "Tershnjaku")
x.printname()


print("Use the super() Function")
#Use the super() Function

class Student(Person):
  def __init__(self, fname, lname):
    super().__init__(fname, lname)
    self.graduationyear = 2020
    
x = Student("Arianit", "Tershnjaku")
print(x.graduationyear)

#Add Methods
print("Add Methods")

class Student(Person):
  def __init__(self, fname, lname, year):
    super().__init__(fname, lname)
    self.graduationyear = year

  def welcome(self):
    print("Welcome", self.firstname, self.lastname, "to the class of", self.graduationyear)

x = Student("Arianit", "Tershnjaku", 2020)
x.welcome()

x1 = Student("Malart", "Peqani", 2028)
x1.welcome()