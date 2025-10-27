import numpy as np
import matplotlib.pyplot as plt

for indice in range(1, 2, 1):
    nome_import = "Odometria misura numero " + str(indice) + ".npy"
    posizione_robot = np.load(nome_import)
    posizioni_x = []
    posizioni_y = []
    for tempo in range(0, len(posizione_robot), 1):
        posizioni_x.append(posizione_robot[tempo][0])
        posizioni_y.append(posizione_robot[tempo][1])

    plt.plot(posizioni_x, posizioni_y, label="Misura" + str(indice - 5))
plt.legend()
plt.title("Traiettorie ricavate da odometria")
plt.grid()
plt.show()
