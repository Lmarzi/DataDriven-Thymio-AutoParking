import numpy as np
import matplotlib.pyplot as plt

costante = 1 * 0.01
tutte_velocita = []
lunghezze_array = []
for indice in range(7, 12, 1):
    nome_import = (np.load("Misura numero " + str(indice) + ".npy")).T
    velocita_sinistra = nome_import[0].T
    velocita_destra = nome_import[1].T
    indice_zero = 0
    for item in velocita_sinistra:
        if item == 0:
            indice_zero += 1
        else:
            break
    velocita_sinistra_nozeri = velocita_sinistra[(indice_zero):len(velocita_sinistra)]
    velocita_destra_nozeri = velocita_destra[(indice_zero):len(velocita_sinistra)]
    lunghezze_array.append(len(velocita_sinistra_nozeri))
    tutte_velocita.append([velocita_sinistra_nozeri, velocita_destra_nozeri])
    tempi = nome_import[2] * costante
    n = len(velocita_sinistra_nozeri)
    t = np.linspace(0, n * 0.01, n)
    plt.plot(t, velocita_sinistra_nozeri, label="Misura" + str(indice - 6), linewidth=0.5)
min = np.amin(np.array(lunghezze_array))
tempi = []
velocita_media_array = []
for tempo in range(0, min, 1):
    velocita_media = 0
    velocita_media_destra = 0
    velocita_media_sinistra = 0
    for misura in range(0, len(tutte_velocita), 1):
        velocita_media_sinistra += tutte_velocita[misura][0][tempo] / 5
        velocita_media_destra += tutte_velocita[misura][1][tempo] / 5
    velocita_media_array.append([velocita_media_sinistra, velocita_media_destra])
    tempi.append(tempo * costante)
print(velocita_media_array)
velocita_media_array = np.array(velocita_media_array)
np.save("Veocita_nominale_2_a", velocita_media_array)
plt.plot(tempi, velocita_media_array.T[0], label="Velocità media", linewidth=2)
plt.title("Velocità motore sinistro")
plt.legend()
plt.grid()
plt.show()
