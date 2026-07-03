"""
Method është funksion brenda class-it

Pra:

Function = jashtë class
Method = brenda class

dallimi mes function dhe method:
Function = i pavarur
Method = i lidhur me class/object
"""
class Student:

    def pershendetje(self):
        print("Pershendetje!")

s1 = Student() #e thërret object-i
s1.pershendetje() #është method

class Student:

    def show(self, emri): #method
        print("Emri:", emri)

s1 = Student()
s1.show("Ardi")

class Student:

    def emri_i_plot(self, emri, mbiemri):
        return emri + " " + mbiemri #kthen vlere

s1 = Student()

rezultati = s1.emri_i_plot("Ardi", "Krasniqi")

print(rezultati)

#constructor është një method i veçantë që ekzekutohet automatikisht kur krijohet një objekt nga class
class Student:
    def __init__(self, emri, mbiemri):#constructor
        self.emri = emri #self: vet objekti
        self.mbiemri = mbiemri

s1 = Student("Ardi", "Krasniqi")#krijimi i objektit me vlera të ndryshme

print(s1.emri, s1.mbiemri) #printimi i vlerave të objektit s1
