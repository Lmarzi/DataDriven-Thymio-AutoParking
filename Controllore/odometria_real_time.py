import numpy as np

distanza_ruote = 9.4 * 0.01  # distanza tra le due ruote in metri
tempo_unita_misura = 0.01  # Il periodo corrispondente ad un segnale di 100hz è 0.01 sec

# OCCHIO DA SISTEMARE
# Costanti di proporzionalità tra velocità in unità di misura robot e velocità
# unità di misura m/s
costante_datomotori_velocitafisica = 0.01 * np.array(
    [0.048879359, 0.043209112, 0.040482443, 0.0380325, 0.036219548, 0.035418081,
     0.0339844, 0.03339,
     0.033333])


# Esprime la velocità in m/s in unità misura del robot
def velocita_robot(vel_fisica):
    velocita_rob = 0
    velocita = abs(vel_fisica)
    if velocita <= 10 * costante_datomotori_velocitafisica[0]:
        velocita_rob = vel_fisica * (1 / costante_datomotori_velocitafisica[0])
    elif velocita <= 17 * costante_datomotori_velocitafisica[1]:
        velocita_rob = vel_fisica * (1 / costante_datomotori_velocitafisica[1])
    elif velocita <= 25 * costante_datomotori_velocitafisica[2]:
        velocita_rob = vel_fisica * (1 / costante_datomotori_velocitafisica[2])
    elif velocita <= 50 * costante_datomotori_velocitafisica[3]:
        velocita_rob = vel_fisica * (1 / costante_datomotori_velocitafisica[3])
    elif velocita <= 75 * costante_datomotori_velocitafisica[4]:
        velocita_rob = vel_fisica * (1 / costante_datomotori_velocitafisica[4])
    elif velocita <= 100 * costante_datomotori_velocitafisica[5]:
        velocita_rob = vel_fisica * (1 / costante_datomotori_velocitafisica[5])
    elif velocita <= 150 * costante_datomotori_velocitafisica[6]:
        velocita_rob = vel_fisica * (1 / costante_datomotori_velocitafisica[6])
    elif velocita <= 200 * costante_datomotori_velocitafisica[7]:
        velocita_rob = vel_fisica * (1 / costante_datomotori_velocitafisica[7])
    elif velocita <= 250 * costante_datomotori_velocitafisica[8]:
        velocita_rob = vel_fisica * (1 / costante_datomotori_velocitafisica[8])
    elif velocita <= 500 * costante_datomotori_velocitafisica[8]:
        velocita_rob = vel_fisica * (1 / costante_datomotori_velocitafisica[8])

    return int(round(velocita_rob))


# Esprime la velocità in unità misura del robot in m/s
def velocita_reale(velocita_da_robot):
    velocita_fisica = 0
    velocita = abs(velocita_da_robot)
    if velocita <= 10:
        velocita_fisica = velocita_da_robot * costante_datomotori_velocitafisica[0]
    elif velocita <= 17:
        velocita_fisica = velocita_da_robot * costante_datomotori_velocitafisica[1]
    elif velocita <= 25:
        velocita_fisica = velocita_da_robot * costante_datomotori_velocitafisica[2]
    elif velocita <= 50:
        velocita_fisica = velocita_da_robot * costante_datomotori_velocitafisica[3]
    elif velocita <= 75:
        velocita_fisica = velocita_da_robot * costante_datomotori_velocitafisica[4]
    elif velocita <= 100:
        velocita_fisica = velocita_da_robot * costante_datomotori_velocitafisica[5]
    elif velocita <= 150:
        velocita_fisica = velocita_da_robot * costante_datomotori_velocitafisica[6]
    elif velocita <= 200:
        velocita_fisica = velocita_da_robot * costante_datomotori_velocitafisica[7]
    elif velocita <= 250:
        velocita_fisica = velocita_da_robot * costante_datomotori_velocitafisica[8]
    elif velocita <= 500:
        velocita_fisica = velocita_da_robot * costante_datomotori_velocitafisica[8]
    return velocita_fisica


# calcola posizione x_y successiva
def pos_x_y(posizione_precedente, angolo_successivo, velocita_angolare, velocita_mezzeria, intervallo_tempo):
    # questo tipo di integrazione è esatta ma il seguente problema, velocità angolare non può essere nulla
    if abs(velocita_angolare) >= 0.0001:
        x = posizione_precedente[0] + (
                velocita_mezzeria * (np.sin(angolo_successivo) - np.sin(posizione_precedente[2]))) / velocita_angolare
        y = posizione_precedente[1] - (
                velocita_mezzeria * (np.cos(angolo_successivo) - np.cos(posizione_precedente[2]))) / velocita_angolare
    # risolvo il vincolo sulla velocità angolare usando un algoritmo di integrazione meno esatto
    else:
        x = posizione_precedente[0] + velocita_mezzeria * intervallo_tempo * np.cos(
            posizione_precedente[2] + velocita_angolare * intervallo_tempo / 2)
        y = posizione_precedente[1] + velocita_mezzeria * intervallo_tempo * np.sin(
            posizione_precedente[2] + velocita_angolare * intervallo_tempo / 2)
    return [x, y]


# dati misurati : [velocita_sinistra_robot,velocita_destra_robot, numero_cicli_100hz]
# posizione_precedente : [x, y, phi, ascissa_curvilinea, numero_cicli_100hz]
def posizione_nuova(dati_misurati, posizione_precedente):
    velocita_sinistra = velocita_reale(dati_misurati[0])
    velocita_destra = velocita_reale(dati_misurati[1])
    velocita_angolare = (velocita_destra - velocita_sinistra) / distanza_ruote  # da controllare i segni
    velocita_mezzeria = (velocita_sinistra + velocita_destra) / 2
    intervallo_tempo = (dati_misurati[2] - posizione_precedente[4]) * tempo_unita_misura
    angolo_successivo = posizione_precedente[2] + velocita_angolare * intervallo_tempo
    pos_x_y_successiva = pos_x_y(posizione_precedente, angolo_successivo, velocita_angolare, velocita_mezzeria,
                                 intervallo_tempo)
    ascissa_curvilinea = posizione_precedente[3] + np.sqrt(
        np.square(pos_x_y_successiva[0] - posizione_precedente[0]) + np.square(
            pos_x_y_successiva[1] - posizione_precedente[1]))

    posizione_successiva = [pos_x_y_successiva[0], pos_x_y_successiva[1], angolo_successivo, ascissa_curvilinea,
                            dati_misurati[2]]
    return posizione_successiva
