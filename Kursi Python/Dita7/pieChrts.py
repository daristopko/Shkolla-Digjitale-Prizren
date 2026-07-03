import matplotlib.pyplot as plt
import numpy as np

y = np.array([35, 25, 25, 15])#Krijon një array me numra të caktuar që do të përdoren për të krijuar grafikun me vija.
mylabels = ["Python", "Java", "PHP", "JavaScript"]


plt.pie(y, labels = mylabels)#pie() krijon një grafik me formën e një rrethi, ku y janë vlerat për secilën kategori dhe labels janë etiketat për secilën kategori.
plt.show() 

# Explode eshtë një mënyrë për të nxjerrë një pjesë të grafikës së rrethit nga qendra për ta theksuar atë.
y = np.array([35, 25, 25, 15])
mylabels = ["Python", "Java", "PHP", "JavaScript"]
myexplode = [0.2, 0, 0, 0]#myexplode është një listë që përcakton se sa do të "shpërthejë" secila pjesë e grafikës së rrethit. Në këtë rast, pjesa e parë (Python) do të shpërthejë më shumë se pjesët e tjera.
plt.pie(y, labels = mylabels, explode = myexplode)
plt.show() 

#Shadow është një efekt vizual që shton një hije poshtë grafikës së rrethit për ta bërë atë më të dukshëm dhe më tërheqës.
y = np.array([35, 25, 25, 15])
mylabels = ["Python", "Java", "PHP", "JavaScript"]
myexplode = [0.2, 0, 0, 0]

plt.pie(y, labels = mylabels, explode = myexplode, shadow = True)
plt.show() 

#Legend është një shpjegim vizual që tregon se çfarë përfaqësojnë ngjyrat ose simbolet në një grafik. Në këtë rast, legjenda do të tregojë se cilat ngjyra përfaqësojnë secilën kategori në grafikën e rrethit.
y = np.array([35, 25, 25, 15])
mylabels = ["Python", "Java", "PHP", "JavaScript"]

plt.pie(y, labels = mylabels)
plt.legend(title = 'Programming languages')
plt.show() 