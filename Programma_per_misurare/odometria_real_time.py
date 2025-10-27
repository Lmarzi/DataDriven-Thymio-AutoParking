import numpy as np

distanza_ruote = 9.4
tempo_unita_misura = 0.01

# OCCHIO DA SISTEMARE
costante_datomotori_velocitafisica = [0.048879359, 0.043209112, 0.040482443, 0.0380325, 0.036219548, 0.035418081,
                                      0.0339844, 0.03339,
                                      0.033333]


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


# in dati misurati [vr,vd,tempo], pos precedente [x,y,phi,s,tempo]
def posizione_nuova(dati_misurati, posizione_precedente):
    velocita_sinistra = velocita_reale(dati_misurati[0])
    velocita_destra = velocita_reale(dati_misurati[1])
    velocita_angolare = (velocita_destra - velocita_sinistra) / distanza_ruote  # da controllare i segni
    velocita_mezzeria = (velocita_sinistra + velocita_destra) / 2
    intervallo_tempo = (dati_misurati[2] - posizione_precedente[4]) * tempo_unita_misura
    angolo_successivo = posizione_precedente[2] + velocita_angolare * intervallo_tempo
    # da vedere cosa conviene mettere di range
    if abs(velocita_angolare) >= 0.0001:
        x = posizione_precedente[0] + (
                velocita_mezzeria * (np.sin(angolo_successivo) - np.sin(posizione_precedente[2]))) / velocita_angolare
        y = posizione_precedente[1] - (
                velocita_mezzeria * (np.cos(angolo_successivo) - np.cos(posizione_precedente[2]))) / velocita_angolare
    else:
        x = posizione_precedente[0] + velocita_mezzeria * intervallo_tempo * np.cos(
            posizione_precedente[2] + velocita_angolare * intervallo_tempo / 2)
        y = posizione_precedente[1] + velocita_mezzeria * intervallo_tempo * np.sin(
            posizione_precedente[2] + velocita_angolare * intervallo_tempo / 2)

    ascissa_curvilinea = posizione_precedente[3] + np.sqrt(
        np.square(x - posizione_precedente[0]) + np.square(y - posizione_precedente[1]))

    posizione_successiva = [x, y, angolo_successivo, ascissa_curvilinea, dati_misurati[2], dati_misurati[5]]

    return posizione_successiva
