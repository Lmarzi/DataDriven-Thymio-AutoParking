import math
import numpy as np
import matplotlib.pyplot as plt

# Tipi di errori che si possono visualizzare:
# 1. Differenza di angoli tra il giro successivo ed il giro precedente,
#    si lascia secondo_giro =  posizione_robot [ tempo + 5400] (5400 = periodo del giro)
#    si varia il tempo massimo del ciclo for
# 2. Differenza angolo tra primo giro e giro-x, si lascia inviariato il ciclo for.
#    Si modifica pos_rob[tempo+5400*quanti_giri]

posizione_robot = np.load("Dati_non_usati/Dati odometria.npy")
print(posizione_robot)
posizioni_x = []
posizioni_y = []
angolo_primo_1 = []
angolo_secondo_2 = []
buchi_x = []
buchi_y = []
errori = []
errori_angolo = []
tempi = []

# ERRORI ANGOLI TRA GIRO SUCCESSIVO E GIRO PRECEDENTE
for tempo in range(68, 5668, 1):
    primo_giro = posizione_robot[tempo]

    secondo_giro = posizione_robot[tempo + 5490]

    # errore = math.sqrt(
    #   (primo_giro[0] - secondo_giro[0]) * (primo_giro[0] - secondo_giro[0]) + (primo_giro[1] - secondo_giro[1]) * (
    #          primo_giro[1] - secondo_giro[1]))

    angolo_primo = primo_giro[2] * 180 / 3.14
    angolo_primo_1.append(angolo_primo)
    angolo_secondo = secondo_giro[2] * 180 / 3.14 - 360
    angolo_secondo_2.append(angolo_secondo)
    print("Angolo primo", angolo_primo)
    print("Angolo secondo", angolo_secondo)
    errore_angolo = (angolo_secondo - angolo_primo)
    errori_angolo.append(errore_angolo)
    tempi.append(tempo)
    if primo_giro[5] == 1 or secondo_giro[5] == 1:
        buchi_x.append(tempo)
        buchi_y.append(errore_angolo)

# for item in posizione_robot:
#  posizioni_x.append(item[0])
# posizioni_y.append(item[1])
# if item[5] == 1:
#    buchi_x.append(item[0])
#   buchi_y.append(item[1])

plt.plot(tempi, errori_angolo)
plt.plot(tempi, angolo_primo_1)
plt.plot(tempi, angolo_secondo_2)
plt.scatter(buchi_x, buchi_y)

plt.show()
