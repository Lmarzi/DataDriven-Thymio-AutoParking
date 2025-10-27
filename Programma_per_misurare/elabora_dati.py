import matplotlib.pyplot as plt
import numpy as np


# UTILIZZO: Bisogna inserire i file di tipo npy nella directory del programma. Devono avere un nome del tipo array = np.load("Misura numero: " + str(j) + ".npy").
# se si utilizzano nomi diversi bisogna semplicemente cambiare la stringa. 
# l'array nel formato npy deve essere di questa forma [[[],[],..],[[],[],..],..], un array multidimensionale. 
# [[misura0],[misura1],...] dove misura0 = [[dati0,dato1,dato2],[dato0,dato1,dato2],..,[dato0,dato1,dato2]]
# dove dato[2] rappresenta il tempo legato alla misurazione dei dati0,dati1. --> questo formato di array è quello che si ottiene dalla stampa npy in Thymio_GUI
# Il programma permettere di quantificare il numero di buchi/coppie presenti nel set di dati. 
# in particolare quantifica il numero di buchi/coppie di tipo 1,2,3 e quelli maggiori di 3. 
# esempio [1,2,2,4,6,9,14,20,23,27,27,27] 
# buchi[1,1,1,2] 1x(buchi da 1),1x(buchi da 2),1x(buchi da 3), 2x(buchi da più di 3)
# al momento per vedere la lunghezza della sequenza di buchi più lunga è necessario cambiare di volta in volta il parametro di riga 55 if item[0] > 3.
# quindi in questo caso cambierei con, if item[0] == 4 --> vedo output,... if item[0] == 5 --> output = [1,1,1,1], quindi ho un buco da 5
# in modo analogo per le coppie

# funzione per forzare l'array come classe lista invece di np objecy ( forse inutile ?)
def array_plottare(array):
    array_da_plottare = []
    for item in array:
        a = item[0]
        b = item[1]
        c = item[2]
        inserimento = [a, b, c]
        array_da_plottare.append(inserimento)
    return array_da_plottare


def massimo_tempo(array):
    tempo_massimo_array = []
    for item in array:
        numero = item[2]
        if numero < 6000:
            tempo_massimo_array.append(item)
        else:
            return tempo_massimo_array

def data_errori_buchi(errori):
    array_ritorno = [0, 0, 0, 0]
    # print("SONO QUA")
    # print(errori)
    # print("SONO QUI")
    # conta = 0
    for misure in errori:
        data_buchi = [0, 0, 0, 0]
        for item in misure[1]:
            # print(misure[1])
            if item[0] == 1:
                data_buchi[0] += 1
            if item[0] == 2:
                data_buchi[1] += 1
            if item[0] == 3:
                data_buchi[2] += 1
            if item[0] > 3:
                data_buchi[3] += 1
        # print("Data buchi: " + str(conta))
        # print(data_buchi)
        # conta += 1
        for l in range(0, len(array_ritorno), 1):
            array_ritorno[l] = array_ritorno[l] + data_buchi[l]

    return array_ritorno

def data_errori_coppie(errori):
    array_ritorno = [0, 0, 0, 0]
    # print("SONO QUA")
    # print(errori)
    # print("SONO QUI")
    # conta = 0
    for misure in errori:
        data_coppie = [0, 0, 0, 0]
        for item in misure[0]:
            # print(misure[1])
            if item[0] == 1:
                data_coppie[0] += 1
            if item[0] == 2:
                data_coppie[1] += 1
            if item[0] == 3:
                data_coppie[2] += 1
            if item[0] > 3:
                data_coppie[3] += 1
        # print("Data buchi: " + str(conta))
        # print(data_buchi)
        # conta += 1
        for l in range(0, len(array_ritorno), 1):
            array_ritorno[l] = array_ritorno[l] + data_coppie[l]

    return array_ritorno


array_veri = []
# raccoldo gli array in formato npy e gli converto in array liste. [ARRAY INTERO] --> i.esimo=[numero misurazione] --> j-esimo=[jM.R,jM.L,j-numericicli]
for j in range(0, 13, 1):
    if j == 4:
        pass
    else:
        array = np.load("Misura numero: " + str(j) + ".npy")
        array_veri.append(array_plottare(array))

array_definitivo = []
# prendo l'array con misurazione massimo 1 minuti
for item in array_veri:
    array_definitivo.append((massimo_tempo(item)))


# print(array_definitivo[3])
# genero array che mi salva gli errori trovati
# per ogni misura
errori = []
k = 0
for misure in array_definitivo:
    k += 1
    doppia = []
    conta_doppia = 0
    check_doppia = misure[0][2]
    buchi = []
    conta_buchi = 0
    check_buco = misure[0][2]
    for i in range(1, len(misure), 1):
        # and serve per controllare di non avere una doppia, se così fosso avrei
        # [1,2,2,3] allora se sono in posizione 2, ho 2 != 2-1 , mi conterebbe il buco
        # non ha senso, mettendo l'and bisogna garantire 2 != 2 allora ok
        if check_buco != misure[i][2] - 1 and check_buco != misure[i][2]:
            conta_buchi = misure[i][2] - 1 - check_buco
            check_buco = misure[i][2]
            indice_problema = i
            buchi.append([conta_buchi, indice_problema])
            conta_buchi = 0
        else:
            check_buco = misure[i][2]

        if check_doppia == misure[i][2]:
            conta_doppia += 1
        elif check_doppia != misure[i][2]:
            if conta_doppia != 0:
                indice_problema = i
                doppia.append([conta_doppia, indice_problema])
                conta_doppia = 0
            check_doppia = misure[i][2]
        else:
            print("WOWO QUALCOSA DI INSTAPETTATO")
    raccolgo = [doppia, buchi]
    errori.append(raccolgo)

data_errori_buchi = data_errori_buchi(errori)
print("[# buco da 1][# buco da 2][# buco da 3][# buco più di 3]")
print(data_errori_buchi)
print("[# coppie da 1][# coppie da 2][# coppie da 3][# coppie più di 3]")
data_errori_coppie = data_errori_coppie(errori)
print(data_errori_coppie)

# ogni i-esimo elemento di questo array rappresenta il numero di campioni misurati in 1 minuti nella misura i-esima
campioni_misurati = []
for item in array_definitivo:
    campioni_misurati.append(len(item))

print(campioni_misurati)

somma_campioni_effettiva = 0
for item in campioni_misurati:
    somma_campioni_effettiva += item
print(somma_campioni_effettiva)

somma_buchi = data_errori_buchi[0] + 2 * data_errori_buchi[1] + 3 * data_errori_buchi[2] + 4 * data_errori_buchi[3]
print(somma_buchi)

#bins = [5960, 5980, 6020, 6060, 6080]
#plt.hist(campioni_misurati, bins=bins, color="grey", edgecolor="black")

#plt.show()

