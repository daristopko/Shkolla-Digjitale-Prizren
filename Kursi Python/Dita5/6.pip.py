
"""
Çka është PIP?

PIP është package manager në Python.

Me PIP mund të instalojmë libra (packages) që nuk vijnë brenda Python-it.
Për shembull, për të punuar me imazhe, mund të instalojmë librin Pillow.
Për të punuar me data dhe kohë, mund të instalojmë librin datetime.
Për të punuar me data në format JSON, mund të instalojmë librin json.
Për të punuar me data në format CSV, mund të instalojmë librin csv.etj
."""

print("\n===== Python PIP =====")


# ==============================
# INSTALIMI (në terminal, JO në kod)
# ==============================

# pip install camelcase
# pip list

# ==============================
# PËRDORIMI I PACKAGE
# ==============================

import camelcase #pip install camelcase

# krijojmë objekt nga CamelCase class (CamelCase është class, camelcase është module)
c = camelcase.CamelCase()

# konverton tekstin në CamelCase
result = c.hump('hello_world')

print("Rezultati:")
print(result)
 
import qrcode #pip install qrcode

img = qrcode.make("https://shkolladigjitaleprizren.com") #pip install pillow për me punu me imazhe
img.save("qr.png")