class Student:
    def __init__(self, emri, mbiemri, mosha, nota):
        self.emri = emri
        self.mbiemri = mbiemri
        self.mosha = mosha
        self.nota = nota

    def info(self):
        print(self.emri, self.mbiemri, "-", self.mosha, "vjeç", "- Nota:", self.nota)

    def result(self):
        if self.nota >= 5:
            print(self.emri, "Kaloi")
        else:
            print(self.emri, "Nuk kaloi")


# studentat (objects)
s1 = Student("Ardi", "Hoxha", 15, 7)
s2 = Student("Enes", "Mehmeti", 16, 4)
s3 = Student("Dua", "Gashi", 14, 10)

# shfaqja
s1.info()
s1.result()

s2.info()
s2.result()

s3.info()
s3.result()