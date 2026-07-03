"""
import eshte për me marr funksione, libra (libraries) ose module të gatshme që nuk i shkruan vetë, por i përdor prej jashtë.
Çka është JSON?

JSON (JavaScript Object Notation) është format për me ruajt të dhëna si tekst.

Në Python përdoret për:
- me ruajt të dhëna në file
- me i lexu prapë më vonë
- me i konvertu të dhënat
- me i dërgu në API (web)

dump()  = Shkruan JSON në file.
load()  = Lexon JSON prej file-it.
dumps() = kthen Python dictionary to JSON string
loads() = kthen JSON string to Python dictionary
"""

import json 

print("\n===== 1. PYTHON -> JSON STRING (dumps) =====")

# Python dictionary
student = {
    "emri": "Ardit",
    "mosha": 16,
    "klasa": "10A"
}

# dumps → Python object në JSON string
json_string = json.dumps(student)

print("JSON string:")
print(json_string)


print("\n===== 2. JSON STRING -> PYTHON (loads) =====")

# JSON string
x = '{"emri": "Ardit", "mosha": 16, "klasa": "10A"}'

# loads → JSON string në Python dictionary 
data = json.loads(x)

print("Python dictionary:")
print(data)

print("Emri:", data["emri"])


print("\n===== 3. SAVE NË FILE (dump) =====")

# ruajtje në file
with open("student.json", "w") as file: #w- write (shkruaj)
    json.dump(student, file) #dump → shkruan në file, merr 2 argumente: të dhënat dhe file-in

print("Të dhënat u ruajtën në student.json")


print("\n===== 4. LOAD NGA FILE (load) =====")

# lexim nga file
with open("student.json", "r") as file: #r- read (lexo)
    file_data = json.load(file)

print("Të dhënat nga file:")
print(file_data)