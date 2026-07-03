# Dictionary ruan të dhëna në format key:value (çelës:vlerë)
# Çelësat (keys) duhet të jenë unikë

personi = {
    "first_name": "Kebir",
    "last_name": "Qesko",
    "age": 30
}

# shfaq dictionary komplet
print(personi)

# marrim vlerën sipas key
print(personi["first_name"])

# mënyrë më e sigurt për me marrë vlerë (nuk jep error nëse key nuk ekziston)
print(personi.get("last_name"))

# numri i elementeve në dictionary
print(len(personi))

# kontrollojmë tipin e të dhënave
print(type(personi))

# metoda tjeter për krijimin e dictionary me dict() pa përdorur { }.
laptop = dict(
    name="Lenovo",
    model="ideapad 5",
    color=["Black", "Grey"]
)

# shfaq dictionary
print(laptop)

# marrim vlerën e modelit
print(laptop["model"])

# ndryshojmë vlerën e një key ekzistues
laptop["model"] = "ideapad 3"
print(laptop)

# update përdoret për me ndryshu ose shtuar disa vlera njëkohësisht
laptop.update({"model": "ideapad 4", "RAM": "16GB", "SSD": "256GB"})
print(laptop)

# shtojmë një key të ri
laptop["SSD"] = "512GB"
print(laptop)