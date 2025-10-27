import numpy as np
import matplotlib.pyplot as plt

array = np.load("transitorio_150_100.npy")
velocita_sinistra = array.T[0]
velocita_destra = array.T[1]
costante = 0.01
tempi = array.T[2] * costante

plt.plot(tempi, velocita_sinistra, label="velocita sinistra")
plt.plot(tempi, velocita_destra, label="velocita destra")
plt.plot([0, tempi[len(tempi) - 1]], [100, 100])
plt.plot([0, tempi[len(tempi) - 1]], [150, 150])
# plt.xlim(5.5,5.9)
# plt.ylim(80,180)
plt.title("Transitorio allo scalino")
plt.grid()
velocita_100 = velocita_sinistra[200:430]
print("Media sx", np.average(velocita_100))
print("std sx", np.std(velocita_100))
velocita_150 = velocita_sinistra[600:1200]
print("Media sx", np.average(velocita_150))
print("std sx", np.std(velocita_150))
velocita_100 = velocita_destra[200:430]
print("Media dx", np.average(velocita_100))
print("std dx", np.std(velocita_100))
velocita_150 = velocita_destra[600:1200]
print("Media dx", np.average(velocita_150))
print("std dx", np.std(velocita_150))
plt.legend()
plt.show()
