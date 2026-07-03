"""
Çka janë Modules?

Modules janë file Python që përmbajnë funksione,
variabla ose kode që mund t'i përdorim në programe tjera.

Mendoje si një “library” me kode të gatshme.
"""

print("\n===== Python Modules =====")

# ==============================
# IMPORTIMI I MODULE
# ==============================

# importojmë module me alias (shkurtimi)
#mn është “shkurtim” që i referohet modulit modulName
#modulName.py është file që përmban funksionin text() dhe dictionary person
import modulName as mn

# thërrasim funksionin text() nga module
mn.text("Kebir")

# ==============================
# VARIABLES NGA MODULE
# ==============================

# marrim vlerën "name" nga dictionary person
a = mn.person["name"]

print(a)

# ==============================
# FROM ... IMPORT ...
# ==============================

# importojmë vetëm variablën person
from modulName import person

print(person["age"], "vjeç",person["name"])


# ==============================
# BUILT-IN MODULES
# ==============================

# module i gatshëm në Python
import platform

# system() -> tregon sistemin operativ
x = platform.system()

print(x)

# ==============================
# dir() FUNCTION
# ==============================

# dir() -> tregon krejt funksionet/objektet e module
x = dir(platform)

print(x)