import numpy as np
import matplotlib.pyplot as plt
import math

# L'alogritmo si basa sull'ipotizzare il moto del robot come un moto piano.
# Si conoscono la velocità di due suoi punti, quindi si può calcolare tutto il suo campo di velocità.
# L'input deve essere un array salvato in formato npy del tipo:
# [[motor.left.speed, motor.right.speed, #cicli_100hz],...,[motor.left.speed, motor.right.speed, #cicli_100hz]]
# Il file deve essere all'interno della stessa cartella file phyton


dati_misurati = np.load(
    "Misura numero: 0.npy")  # Da modificare nel caso in cui si vogliano caricare l'array per altra via
intervallo_tempo = 0.01  # è il periodo associato a 100hz, se si usa un altro contatore bisogna cambiare tale valore.
distanza_ruote = 9.5  # in cm
distanza_appoggio_mezzeria = 6  # abbastanza indifferente ai fini dei calcoli, si può prendere
# un qualunque punto, basta che stia sull'asse polare.

costante_datomotori_velocitafisica = 0.03333333
# significa motor.rigth.speed = 300 --> ruota destra velocità lineare 10 cm/s

# dati_prova = [[70, 90, 0], [90, 70, 1], [50, -70, 3], [-30, 50, 4], [-50, 30, 6], [60, -30, 7]]
# dati_prova = [[70, 70, 0], [70, 70, 1], [70, 70, 3], [70, 70, 4], [70, 70, 6], [70, 70, 7]]


dati_caratteristici = []


# aggiungere punti caratteristici per confronto con i dati ottenuti dal seguente algoritmo di odometria


def posizione_cir_velocita_angolare(dati):
    # Viene calcolata la posizione del centro d'istantanea rotazione rispetto alla ruota sinistra del robot
    # Viene calcolata la velocità angolare del robot rispetto all'asse perpendicolare al piano e passante per il cir
    # Attenzione che non viene considerato il caso di entrambe le velocità negative
    velocita_sinistra = dati[0] * costante_datomotori_velocitafisica
    velocita_destra = dati[1] * costante_datomotori_velocitafisica
    # l'algoritmo iniziale non teneva conto dei 3 seguenti casi. Si è deciso di aggirare il problema
    # scostante le misure di una piccolissima quantità, l'errore è trascurabile rispetto alle altre approssimazioni
    # --> se ci sono problemi di precisione nell'algoritmo, considerare i casi precisi
    if velocita_destra == 0:
        velocita_destra = 0.0001
    if velocita_sinistra == 0:
        velocita_sinistra = 0.0001
    if abs(velocita_destra) == abs(velocita_sinistra):
        velocita_destra = velocita_destra + 0.0001
    # print("Queste sono le velocità in cm/s delle due ruote [sinistra,destra]")
    # print([velocita_sinistra, velocita_destra])
    vettore_coordinate_polari = []
    velocita_angolare = 0
    if velocita_destra > velocita_sinistra > 0:
        distanza_ruota_sinistra_cir = distanza_ruote / ((velocita_destra / velocita_sinistra) - 1)
        vettore_coordinate_polari = [0, -distanza_ruota_sinistra_cir]
        velocita_angolare = abs(velocita_sinistra / distanza_ruota_sinistra_cir)
    elif velocita_sinistra > velocita_destra > 0:
        distanza_ruota_sinistra_cir = distanza_ruote / (1 - (velocita_destra / velocita_sinistra))
        vettore_coordinate_polari = [0, distanza_ruota_sinistra_cir]
        velocita_angolare = -1 * abs(velocita_sinistra / distanza_ruota_sinistra_cir)
    elif (velocita_sinistra > 0 > velocita_destra) and (abs(velocita_destra) > abs(velocita_sinistra)):
        distanza_ruota_sinistra_cir = distanza_ruote / (1 + (abs(velocita_destra) / velocita_sinistra))
        velocita_angolare = -1 * abs(velocita_sinistra / distanza_ruota_sinistra_cir)
        vettore_coordinate_polari = [0, distanza_ruota_sinistra_cir]
    elif (velocita_destra > 0 > velocita_sinistra) and (abs(velocita_destra) > abs(velocita_sinistra)):
        distanza_ruota_sinistra_cir = distanza_ruote / (1 + (velocita_destra / abs(velocita_sinistra)))
        velocita_angolare = abs(velocita_sinistra / distanza_ruota_sinistra_cir)
        vettore_coordinate_polari = [0, distanza_ruota_sinistra_cir]
    elif (velocita_destra > 0 > velocita_sinistra) and (abs(velocita_sinistra) > abs(velocita_destra)):
        distanza_ruota_sinistra_cir = distanza_ruote / (1 + (velocita_destra / abs(velocita_sinistra)))
        velocita_angolare = abs(velocita_sinistra / distanza_ruota_sinistra_cir)
        vettore_coordinate_polari = [0, distanza_ruota_sinistra_cir]
    elif (velocita_sinistra > 0 > velocita_destra) and (abs(velocita_sinistra) > abs(velocita_destra)):
        distanza_ruota_sinistra_cir = distanza_ruote / (1 + (abs(velocita_destra) / velocita_sinistra))
        velocita_angolare = -1 * abs(velocita_sinistra / distanza_ruota_sinistra_cir)
        vettore_coordinate_polari = [0, distanza_ruota_sinistra_cir]

    return [vettore_coordinate_polari, velocita_angolare]


def velocita_mezzeria(dati):
    # mezzeria si intende la velocità del punto intermedio alle due ruote
    distanza_mezzeria_cir = -1 * (distanza_ruote / 2) + dati[0][1]
    velocita = [-1 * dati[1] * distanza_mezzeria_cir, 0]
    return velocita


def velocita_appoggio(dati):
    distanza_mezzeria_cir = -1 * (distanza_ruote / 2) + dati[0][1]
    velocita = [-1 * dati[1] * distanza_mezzeria_cir,
                dati[1] * distanza_appoggio_mezzeria]  # sono ortogonali le due componenti
    return velocita


def trasformazione_polare_cartesiane(vettore_polare, angol):
    coordinata_x = vettore_polare[0] * math.cos(angol) - vettore_polare[1] * math.sin(angol)
    coordinata_y = vettore_polare[0] * math.sin(angol) + vettore_polare[1] * math.cos(angol)
    return [coordinata_x, coordinata_y]


# posizione_iniziale è array [x,y], velocita_cartesiana [vx,vy], tempo = int
def nuova_posizione_cartesiana(posizione_iniziale, velocita_cartesiana, tempo_intervallo):
    posizione_finale = [posizione_iniziale[0] + velocita_cartesiana[0] * tempo_intervallo,
                        posizione_iniziale[1] + velocita_cartesiana[1] * tempo_intervallo]
    return posizione_finale


def calcolo_punto_su_asse_polare(posizione_riferimento, distanza_centro, angol):
    posizione = [posizione_riferimento[0] + distanza_centro * math.cos(angol),
                 posizione_riferimento[1] + distanza_centro * math.sin(angol)]

    return posizione


def calcolo_angolo(posizione_riferimento, posizione_punto_vecchio_riferimento):
    posizione_punto_nuovo_riferimento = [posizione_punto_vecchio_riferimento[0] - posizione_riferimento[0],
                                         posizione_punto_vecchio_riferimento[1] - posizione_riferimento[1]]
    angol = math.atan2(posizione_punto_nuovo_riferimento[1], posizione_punto_nuovo_riferimento[0])
    return angol


velocita_coordinate_polari_tempo = []
for item in dati_misurati:
    cir_velocita_angolare = posizione_cir_velocita_angolare(item)
    velocita_coordinate_polari_tempo.append(
        [velocita_mezzeria(cir_velocita_angolare), velocita_appoggio(cir_velocita_angolare), item[2]])

posizioni = [
    [0, -30, 0, 0]]  # posizione iniziale del robot rispetto al sistema di riferimento scelto [x,y,angolo,ascissa_curvi]
ascissa_curvilinea = 0
for i in range(0, len(velocita_coordinate_polari_tempo) - 1, 1):  # ho messo il -1 per non avere problemi con intervallo
    #
    angolo = posizioni[i][2]
    velocita_g_i = trasformazione_polare_cartesiane(velocita_coordinate_polari_tempo[i][0], angolo)
    velocita_h_i = trasformazione_polare_cartesiane(velocita_coordinate_polari_tempo[i][1], angolo)
    intervallo = (velocita_coordinate_polari_tempo[i + 1][2] - velocita_coordinate_polari_tempo[i][
        2]) * intervallo_tempo
    posizione_g_i = nuova_posizione_cartesiana([posizioni[i][0], posizioni[i][1]], velocita_g_i, intervallo)
    posizione_h_iniziale = calcolo_punto_su_asse_polare([posizioni[i][0], posizioni[i][1]], distanza_appoggio_mezzeria,
                                                        angolo)
    posizione_h_i = nuova_posizione_cartesiana([posizione_h_iniziale[0], posizione_h_iniziale[1]], velocita_h_i,
                                               intervallo)
    angolo_i = calcolo_angolo(posizione_g_i, posizione_h_i)
    if angolo_i < 0:
        # impongo l'angolo sempre positivo
        angolo_i = angolo_i + 2 * math.pi
    # somma la distanza tra due punti successivi
    ascissa_curvilinea = ascissa_curvilinea + math.sqrt(
        (posizioni[i][0] - posizione_g_i[0]) * (posizioni[i][0] - posizione_g_i[0]) + (
                posizioni[i][1] - posizione_g_i[1]) * (posizioni[i][1] - posizione_g_i[1]))
    posizioni.append([posizione_g_i[0], posizione_g_i[1], angolo_i, ascissa_curvilinea])
posizioni_x = []
posizioni_y = []
angoli = []
ascisse = []

for item in posizioni:
    posizioni_x.append(item[0])
    posizioni_y.append(item[1])
    angoli.append(item[2] * 180 / 3.14)
    ascisse.append(item[3])

# print(ascisse)
# print(angoli)
# print(ascisse[len(ascisse) - 1]) #distanza totale percorsa

plt.scatter(posizioni_x, posizioni_y, s=0.5, c='green', marker='o', edgecolors="black", linewidths=1, alpha=0.75)

# --- GRAFICO DI PER CONFRONTO ---
theta = np.linspace(0, 2 * np.pi, 200)

radius = 30

a = radius * np.cos(theta)
b = radius * np.sin(theta)

plt.scatter(a, b, s=0.5, c='green', marker='o', edgecolors="red", linewidths=1, alpha=0.75)
# plt.xlim(-1,1)


plt.show()
