import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.linalg import inv
import odometria_real_time as odr
import os


# titolo deve essere una stringa
def salva_dati(numpy_array, nomecartella, titolo):
    df = pd.DataFrame(numpy_array)
    file_name = os.path.join(nomecartella, titolo + ".csv")
    df.to_csv(file_name, index=False)


def crea_cartella(titolo):
    i = 0
    nome = titolo + str(i)
    while True:
        if os.path.exists(nome):
            nome = titolo + str(i)
        else:
            break
        i = i + 1
    os.makedirs(nome)
    return nome


# dati misurati : [velocita_angolare,velocita_mezzeria, periodo_campionamento]
# posizione_precedente : [x, y, phi]
def nuova_posizione(velocita_tempo, posizione_precedente, step):
    velocita_angolare = velocita_tempo[1]  # da controllare i segni
    velocita_mezzeria = velocita_tempo[0]
    intervallo_tempo = step
    angolo_successivo = posizione_precedente[2] + velocita_angolare * intervallo_tempo
    pos = odr.pos_x_y(posizione_precedente, angolo_successivo, velocita_angolare, velocita_mezzeria, intervallo_tempo)
    pos_x = pos[0]
    pos_y = pos[1]
    posizione_successiva = [pos_x, pos_y, angolo_successivo]

    return posizione_successiva


# velocità in modello uniciclo a velocità in modello reale
def mezzeria_angolare_to_velocita_motori(velocita_mezzeria, velocita_angolare):
    velocita_destra = (distanza_ruote * velocita_angolare + 2 * velocita_mezzeria) / 2
    velocita_sinistra = (2 * velocita_mezzeria - distanza_ruote * velocita_angolare) / 2
    return [velocita_sinistra, velocita_destra]


# velocità in modello reale a velocità in modello uniciclo
def velocita_motori_to_mezzeria_angolare(velocita_sinistra, velocita_destra):
    velocita_angolare = (velocita_destra - velocita_sinistra) / distanza_ruote
    velocita_mezzeria = (velocita_sinistra + velocita_destra) / 2
    return [velocita_mezzeria, velocita_angolare]


def sotto_campiona(array, numero_sotto_campionamento):
    array_sotto_campionato = []
    for tempo in range(0, len(array) - numero_sotto_campionamento - 400, numero_sotto_campionamento):
        array_sotto_campionato.append(array[tempo])
    return np.array(array_sotto_campionato)


# Probabilmente si può omettere questa operazione
def tolto_zeri_iniziali(array_numpy):
    conta = 0
    for dato in array_numpy:
        if dato[0] == 0 and dato[1] == 0:
            conta += 1
        else:
            break
    return array_numpy[conta:len(array_numpy)]


# ------- DEFINIZIONE COSTANTI E CARICAMENTO MISURE------
distanza_ruote = odr.distanza_ruote
# T_fil = 0.08  # per 10 hz
T_fil = 0.08
tempo_da_100hz_a_sotto_campionamento = 10
misure = np.load("Veocita_nominale_2.npy")
misure_no_zeri = tolto_zeri_iniziali(misure)
misure_no_zeri = sotto_campiona(misure_no_zeri, tempo_da_100hz_a_sotto_campionamento)
n = len(misure_no_zeri)  # Rappresenta sia il numero di campioni misurati che il numero di cicli
tempo_totale = tempo_da_100hz_a_sotto_campionamento * n * odr.tempo_unita_misura  # numero_di_cicli * periodo_ciclo
tau = tempo_totale / n  # periodo_ciclo --> superfluo
# Posizione iniziale da impostare in modo tale che la traiettoria dello stato finisca in un intorno di [0,0,0]
x_0 = [0.36852, -0.16785, 0]
U_nom = []

# ------- CALCOLO VELOCITA NOMINALI ------
# -1 Per traiettoria speculare all'indietro
# Dal modello "reale" del robot al modello dell'uniciclo
for velocita_robot in misure_no_zeri:
    v_sx = -1 * odr.velocita_reale(velocita_robot[0])
    v_dx = -1 * odr.velocita_reale(velocita_robot[1])
    v_w = velocita_motori_to_mezzeria_angolare(v_sx, v_dx)
    U_nom.append(v_w)
U_nom = np.array(U_nom)

t = np.linspace(0, tempo_totale, n)

# ------- CALCOLO TRAIETTORIA NOMINALE ------
# x è il vettore di stato x = [x,y,phi]
X_nom = [x_0]
x = x_0

for item in U_nom:
    vel = [item[0], item[1]]
    x = nuova_posizione(vel, x, tau)
    x = [x[0], x[1], x[2]]
    X_nom.append(x)
x_fin = x
X_nom = np.array(X_nom)
U_nom = U_nom.T

# ------ INIZIALIZZAZIONE DISTURBI -------
# --2-- [0 0.2] [-0.002,0.0] [0.0,0.01] avanti
# --2-- [0 0.2] [+0.001,0.0] [0.0, -0.005] indietro

U1 = U_nom + np.array([0.0 * np.ones(n), 0.2 * np.exp(-1 * t)])
U2 = U_nom + np.array([+0.003 * np.ones(n), 0.0 * np.exp(-1 * t)])
U3 = U_nom + np.array([0.0 * np.ones(n), -0.005 * np.ones(n)])
X1 = np.zeros((n + 1, 3))
X2 = np.zeros((n + 1, 3))
X3 = np.zeros((n + 1, 3))
pert = 0.01

# ------ TRAIETTORIA DISTURBATA NUMERO 1 ------
x = np.array(x_fin) + np.array([pert, 0, 0])
# Si ricostruisce la traiettoria a partire dallo stato finale della nominale, ovvero dall'inorno di 0
for misura in range(n, -1, -1):
    X1[misura] = x
    vel = [U1[0][misura - 1], U1[1][misura - 1]]
    x = nuova_posizione(vel, x, -tau)

# ------ TRAIETTORIA DISTURBATA NUMERO 2 ------
x = np.array(x_fin) + np.array([0, pert, 0])

for misura in range(n, -1, -1):
    X2[misura] = x
    vel = [U2[0][misura - 1], U2[1][misura - 1]]
    x = nuova_posizione(vel, x, -tau)

# ------ TRAIETTORIA DISTURBATA NUMERO 3 ------
x = np.array(x_fin) + np.array([0, 0, pert])

for misura in range(n, -1, -1):
    X3[misura] = x
    vel = [U3[0][misura - 1], U3[1][misura - 1]]
    x = nuova_posizione(vel, x, -tau)

# ------ LINEARIZZAZIONE E DEFINIZIONE MATRICE K -----
V1 = U1 - U_nom
V2 = U2 - U_nom
V3 = U3 - U_nom
Z1 = X1 - X_nom
Z2 = X2 - X_nom
Z3 = X3 - X_nom
Z_1 = np.array([Z1[0], Z2[0], Z3[0]])
Z_N = np.array([Z1[n], Z2[n], Z3[n]])
# Il vettore deve avere gli elementi minori di 1, serve a verifcare il rango
print(sum(abs(np.dot(inv(Z_1.T), Z_N.T))))
# Applicazione dell'algoritmo di generazione matrice K(t)
K = np.array(np.zeros((n, 2, 3)))
for h in range(0, n, 1):
    v = np.array([V1.T[h], V2.T[h], V3.T[h]])
    z = inv(np.array([Z1[h], Z2[h], Z3[h]]))
    K[h] = np.dot(z, v).T
U_nom = U_nom.T

if __name__ == "__main__":

    # ------- Controllo dei risultati applicando un disturbo alle condizioni iniziali --------
    # ------- si verifca la stabilità del controllore K -----
    delta = 0.03 * (np.ones(3) - 2 * np.random.rand(3))
    # delta = np.zeros(3)
    v_fil = np.zeros(2)
    # --2-- all'indietro T_fil = 0.05
    # --2-- in avanti T_fil = 0.05
    x_reg = x_0 + delta
    X_reg = []
    x = x_0
    for h in range(0, n, 1):
        u = U_nom[h]
        vel = u + np.dot(K[h], (x_reg - X_nom[h]))
        # La velocità generata dal controllore viene fatta passare per un filtro passa-basso
        # evito bruschi cambiamenti di velocità
        v_fil = v_fil + tau * (vel - v_fil) / T_fil
        x_reg = nuova_posizione(v_fil, x_reg, tau)
        X_reg.append(x_reg)
    X_reg = np.array(X_reg)
    nome_cartella = crea_cartella("dati_no_robot ")
    plt.plot(X_nom.T[0], X_nom.T[1], label="nominale")
    salva_dati(X_nom, nome_cartella, "nominale")
    plt.plot(X1.T[0], X1.T[1], label="disturbata 1")
    salva_dati(X_nom, nome_cartella, "disturbata_1")
    plt.plot(X2.T[0], X2.T[1], label="disturbata 2")
    salva_dati(X_nom, nome_cartella, "disturbata_2")
    plt.plot(X3.T[0], X3.T[1], label="disturbata 3")
    salva_dati(X_nom, nome_cartella, "disturbata_3")
    plt.plot(X_reg.T[0], X_reg.T[1], label="da controllore")
    # salva_dati(X_nom, nome_cartella, "controllore_no_robot")
    plt.legend()
    plt.grid()
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot3D(X_nom.T[0], X_nom.T[1], X_nom.T[2], label="nominale")
    ax.plot3D(X1.T[0], X1.T[1], X1.T[2], label="disturbata 1")
    ax.plot3D(X2.T[0], X2.T[1], X2.T[2], label="disturbata 2")
    ax.plot3D(X3.T[0], X3.T[1], X3.T[2], label="disturbata 3")
    # ax.plot3D(X_reg.T[0], X_reg.T[1], X_reg.T[2], label="da controllore")
    plt.legend()
    plt.grid()
    plt.show()
