"""
Class është një model (blueprint) për krijimin e objekteve.

Shembull nga jeta reale:

Class = Makina
Object = BMW, Audi, Mercedes

Pra class tregon:
çfarë të dhënash ka objekti
çfarë mund të bëjë objekti
"""

class Student:
    emri = "Nart"
    mosha = 15

s1 = Student()
print(s1.emri)
print(s1.mosha)

#Ndryshimi i vlerave

class Student:
    emri = "Nart"

s1 = Student()

s1.emri = "Blerim"

print(s1.emri)

#ushtrimi krijo nje class book me title,author dhe printo vlerat e tyre
class Book:
    title = "Harry Potter"
    author = "J.K. Rowling"
b1 = Book()
print(b1.title)
print(b1.author)


class Student:
    def studentat(self, emri, mbiemri): #self do të thotë: objekti vetë (kjo kopje e class-it)
        self.emri = emri
        self.mbiemri = mbiemri

## 3 objects
# krijimi i objekteve me vlera të ndryshme
s1 = Student()
s1.studentat("Ardi", "Krasniqi")
s2 = Student()
s2.studentat("Blerim", "Hoxha")
s3 = Student()
s3.studentat("Elira", "Gashi")

print(s1.emri, s1.mbiemri)
print(s2.emri, s2.mbiemri)
print(s3.emri, s3.mbiemri)
