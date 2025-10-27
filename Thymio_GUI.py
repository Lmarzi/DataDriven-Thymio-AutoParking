import tdmclient.clientasync
from tdmclient import ClientAsync
import tkinter as tk
from tkinter import ttk
import asyncio
import threading
import numpy as np
import odometria_real_time as odr

# Applicazione per comunicare con il robot Thymio.

# Modalità di utilizzo:
# Sono disponibili due modalità di utilizzo:
# 1. Frequenza di campionamento variabile.
# 2. Frequenza di campionamento pari alla frequenza di invio di uno degli eventi all'interno del robot,
#    i quali sono sincronizzati col il clock del processore.

# Al momento è impostata una frequenza di campionamento pari alla frequenza dell'evento motor (100hz).
# Per impostare modalità variabile togliere i cancelletti dalla riga 67-69 e aggiungere cancelletti alla riga 90

# Funzionamento:
# 1. Inserire il dongle wireless del Thymio e Aprire il robot Thymio.
# 2. Avviare Thymio Suite.
# 3. Avviare il programma.
# 4. Impostare la velocità di base del Thymio. Un'alta velocità può influenzare la fluidità del movimento
#    del robot lungo la linea nera.
# 5. Avvia l'algoritmo di inseguimento della linea nera.
# 6. Imposta il client in ascolto. Quando il client è in ascolto, riceve gli eventi trasmessi dal robot.
#    Al nuovo clic del pulsante, la misura viene salvata e pronta per essere stampata nel tab di stampaggio.
# 7. Esistono due modalità di stampaggio: formato TXT e formato NumPy.

# ATTENZIONE:
# 1.Attualmente, stiamo tenendo traccia del tempo usando la variabile "num_100hz".
#   Questa variabile può assumere al massimo il valore di 32767, circa 5 minuti e 30 secondi.
#   Una misurazione può durare al massimo tale periodo.
#   Per fare più misurazione mantenendo aperto il client si può usare il bottone "reset".


aseba_program = """
var statoProgramma = 0
var minimo = 1023
var maxi = 0
var mean = 512
var vari = 512
var ireg = 0
var p1 = 0
var speed = 0
var ndev = 0
var SIGMA = 100
var preg = 0
var num_100hz = 0
var p2 = 0

onevent algoritmoInFunzione
 if statoProgramma == 0 then
  statoProgramma = 1
 else 
  statoProgramma = 0
 end

onevent setFrequency
 timer.period[0] = event.args[0]

onevent setSpeed
 speed = event.args[0]

onevent timer0
 #da vedere se questo if porta a delle latenze nell'invio
 #if statoProgramma == 1 then
  #emit velocitaMotori [motor.left.speed, motor.right.speed, num_100hz]
 #end

onevent reset
 statoProgramma = 0
 minimo = 1023
 maxi = 0
 mean = 512
 vari = 512
 ireg = 0
 p1 = 0
 speed = 0
 ndev = 0
 preg = 0
 motor.right.target = 0
 motor.left.target = 0
 timer.period[0] = 0
 num_100hz = 0

onevent motor
 if statoProgramma == 1 then
  num_100hz=num_100hz+1
  emit velocitaMotori [motor.left.speed, motor.right.speed, num_100hz, motor.left.target,motor.right.target]
 end

onevent prox
 p2 = prox.ground.delta[0]
 if p2 < 500 then
  emit startStop [num_100hz]
  end
 if statoProgramma == 1 then
  p1 = prox.ground.delta[1]
  callsub statistics
  call math.muldiv(ndev,SIGMA,p1-mean,vari)
  if abs(ndev) < SIGMA then
   preg = 60*ndev/100   #regolazione P, coefficiente ottenuto da Ziegler
   ireg = ireg + 10*preg/30   #regolazione I, coefficiente ottenuto da Ziegler
    if abs(ireg) > 200 then
     ireg = ireg - 10*preg/30
    end
   motor.left.target = speed + (preg+ireg)
   motor.right.target = speed - (preg+ireg)
  else #il robot ha perso la traccia, ruota su se stesso fino a ritrovarla 
   ireg = 0
   motor.left.target = ndev/2
   motor.right.target = -1*ndev/2
  end
 #emit velocitaMotori [motor.left.speed, motor.right.speed, num_100hz, motor.left.target,motor.right.target]
 end

sub statistics
 call math.max(maxi,maxi,p1)
 call math.min(minimo,minimo,p1)
 if maxi-minimo > 400  then  #CALIBRAZIONE INIZIALE 
  call math.muldiv(vari,45,maxi-minimo,100)
  mean = (minimo+maxi)/2  #valore medio gradiente
 end

"""
global node, client
salvataggio_misure = []
dati_motori = []
# Dati iniziale [xg,yg,phi,s,t,packetloss]
dati_iniziali = []
salvataggio_odometria = []
dati_odometria = []
primo_ciclo = True
# costante_togliere = 0
frequenza_campionamento = 0
event = threading.Event()
event.set()


def elabora_array(array):
    costante_da_togliere = array[0][2]  # in modo tale che quando scrivo i dati, il primo tempo è 0
    print(array)
    for item in array:
        item[2] = item[2] - costante_da_togliere
    return array


def stampa_odometria():
    # print(dati_odometria)
    indice_selezionato = quale_misurazione_stampare.current()
    array_da_stampare = salvataggio_odometria[indice_selezionato]
    costante_da_togliere = array_da_stampare[0][4]
    for item in array_da_stampare:
        item[4] = item[4] - costante_da_togliere
    # print(dati_odometria)
    print("Ho tolto la costante", costante_da_togliere)
    string_titolo_file = "Odometria misura numero " + str(indice_selezionato)
    np.save(string_titolo_file, array_da_stampare)


def stampa_numpy():
    indice_selezionato = quale_misurazione_stampare.current()
    array_da_salvare = elabora_array(salvataggio_misure[indice_selezionato])
    np.save("Misura numero " + str(indice_selezionato), array_da_salvare)


def stampa_dati():  # da vedere come fare la formattazione
    global salvataggio_misure
    # print(salvataggio_misure)
    indice_selezionato = quale_misurazione_stampare.current()
    array_da_salvare = elabora_array(salvataggio_misure[indice_selezionato])
    string_titolo_file = "File misura numero " + str(indice_selezionato) + ".txt"

    try:
        with open(string_titolo_file, 'w') as file:
            for item in array_da_salvare:
                i = 0
                for j in range(0, 3, 1):
                    if i == 0 or i == 1:
                        file.write(str(item[j]) + ',')
                        i = i + 1
                    else:
                        file.write(str(item[j]) + "\n")
                        i = 0
    except IOError:
        print('Errore durante il salvataggio dei dati nel file.')
    print("finito stampa ")
    return


def calcolo_odometria(dati_motori_no_buchi):
    global dati_odometria
    # -1 perchè ho la posizione iniziale
    nuovi_dati = len(dati_motori_no_buchi) - (len(dati_odometria) - 1)
    for pacchetto in range(0, nuovi_dati, 1):
        posizione_precedente = dati_odometria[len(dati_odometria) - 1]
        dato_misura = dati_motori_no_buchi[len(dati_motori_no_buchi) - nuovi_dati + pacchetto]
        posizione_nuova = odr.posizione_nuova(dato_misura, posizione_precedente)
        dati_odometria.append(posizione_nuova)
    pass


def calcolo_velocita_con_target(velocita_precedenti, target):
    if target == 0:
        # così vado nel verso giusto
        target = -1 * velocita_precedenti[1]
    delta = abs(velocita_precedenti[0] - velocita_precedenti[1])
    velocita_calcolate = velocita_precedenti[0] + delta * abs(target) / target
    return velocita_calcolate


def velocita_mancante(misura_precedente, misura_due_volte_precedente, velocita_target):
    velocita_sinistra_precedenti = [misura_precedente[0], misura_due_volte_precedente[0]]
    velocita_destra_precedenti = [misura_precedente[1], misura_due_volte_precedente[1]]
    velocita_sinistra_successiva = calcolo_velocita_con_target(velocita_sinistra_precedenti, velocita_target[0])
    velocita_destra_successiva = calcolo_velocita_con_target(velocita_destra_precedenti, velocita_target[1])
    return [velocita_sinistra_successiva, velocita_destra_successiva]


def aggiungi_dato_misurato_e_calcolo_odometria(data_evento):
    global dati_motori, dati_iniziali
    # [vel_sin,vel_dest,tempo,vel_target_sin,vel_target_destra]
    # lo 0 indica che la misura è buona
    misura_iesima = [data_evento[0], data_evento[1], data_evento[2], data_evento[3], data_evento[4], 0]
    quanti_misure = len(dati_motori)
    if quanti_misure == 0:
        dati_motori.append(misura_iesima)
        print([data_evento[2] - 1])
        x = dati_iniziali[0]
        y = dati_iniziali[1]
        phi = dati_iniziali[2]
        dati_odometria.append([x, y, phi, 0, data_evento[2] - 1, 0])
        calcolo_odometria(dati_motori)
        return
    tempo_precedente = dati_motori[len(dati_motori) - 1][2]
    buchi = data_evento[2] - tempo_precedente
    if quanti_misure == 1 and buchi > 1:
        velocita_target_sinistra = data_evento[3] + 1
        velocita_target_destra = data_evento[4] + 1
        for quanti_buchi in range(1, buchi, 1):
            misura_precedente = dati_motori[len(dati_motori) - 1]
            velocita_sinistra_successiva = (misura_precedente[0] + velocita_target_sinistra) / 2 + misura_precedente[0]
            velocita_destra_successiva = (misura_precedente[1] + velocita_target_destra) / 2 + misura_precedente[1]
            dati_motori.append(
                [velocita_sinistra_successiva, velocita_destra_successiva, tempo_precedente + quanti_buchi,
                 data_evento[3], data_evento[4], 1])
        dati_motori.append(misura_iesima)
        calcolo_odometria(dati_motori)
        return
    # questo if probabilmente è di troppo
    if buchi > 0:
        velocita_target_sinistra = data_evento[3]
        velocita_target_destra = data_evento[4]
        for quanti_buchi in range(1, buchi, 1):
            misura_precedente = dati_motori[len(dati_motori) - 1]
            # Attenzione problema quando ho il buco subito all'inizio?
            misura_due_volte_precedente = dati_motori[len(dati_motori) - 2]
            velocita_calcolate = velocita_mancante(misura_precedente, misura_due_volte_precedente,
                                                   [velocita_target_sinistra, velocita_target_destra])
            # 1 indica che la misura è calcolata
            dati_motori.append(
                [velocita_calcolate[0], velocita_calcolate[1], tempo_precedente + quanti_buchi, data_evento[3],
                 data_evento[4], 1])
    dati_motori.append(misura_iesima)
    calcolo_odometria(dati_motori)


# FORSE DA METTERE IN ASYNC PER GARANTIRE DI FARE PRIMA SALVATAGGIO MISURE E POI SALVATAGGIO ODOMETRIA
# Questo serve se inserisco nell'algoritmo di odometria il salvataggio misure
def elaborazione_evento(nodo, nome_evento, data_evento):
    # aggiunto event.is_set() per evitare di raccogliere dati nel tempo che ci mette al client di uscire dall'ascolto
    if nome_evento == "velocitaMotori" and event.is_set():
        aggiungi_dato_misurato_e_calcolo_odometria(data_evento)
    if nome_evento == "startStop" and event.is_set():
        print("Ecco lo start", data_evento[0])


def set_frequency():
    # frequency = entry_frequency.get()
    # if frequency.isdigit():
    #    asyncio.run(set_frequency_async(int(frequency)))
    # else:
    #    print("Inserire un valore valido di frequenza")
    pass


async def set_frequency_async(frequency):
    tempo_ms = (1 / frequency) * 1000  # trasformo la frequenza in periodo ms, così vuole il robot
    print(int(tempo_ms))
    await node.send_events({"setFrequency": [int(tempo_ms)]})  # aseba vuole solo interi


def set_speed():  # è la speed di base del robot
    speed = entry_speed.get()
    # magari da mettere un range di speed accettabile
    if speed.isdigit():
        asyncio.run(set_speed_async(int(speed)))
    else:
        print("Inserire un valore valido di velocità")


async def set_speed_async(speed):
    global node
    await node.send_events({"setSpeed": [speed]})


def send_reset():
    asyncio.run(send_reset_async())


async def send_reset_async():
    await node.send_events({"reset": []})


def send_change_state_algorithm():
    # permette di attivare o meno l'algoritmo segui linea nera
    testo = button_stato_algoritmo['text']
    if testo == "Follow line OFF":
        button_stato_algoritmo.config(text="Follow line ON")
    else:
        button_stato_algoritmo.config(text="Follow line OFF")
    asyncio.run(send_change_state_algorithm_async())


async def send_change_state_algorithm_async():
    await node.send_events({"algoritmoInFunzione": []})


def salva_misura():
    # procede al salvataggio della misura nel database salvataggio_misure
    global dati_motori, salvataggio_misure, dati_odometria, salvataggio_odometria
    salvataggio_misure.append(dati_motori)
    salvataggio_odometria.append(dati_odometria)
    dati_odometria = []
    dati_motori = []
    update_combobox()


def update_combobox():
    # aggiorna il combobox nel momento in cui aumentiamo le misure fatte di una
    misure_fatte = len(salvataggio_misure)
    opzioni_aggiornate = []
    for i in range(0, misure_fatte, 1):
        opzioni_aggiornate.append("Misura numero: " + str(i + 1))
    quale_misurazione_stampare['values'] = opzioni_aggiornate


def set_starting_position():
    global dati_iniziali
    x = float(entry_initial_condition_x.get())
    y = float(entry_initial_condition_y.get())
    phi = float(entry_initial_condition_phi.get())
    dati_iniziali = [x, y, phi, 0, 0, 0]

    # da entrare x,y,phi


def setting_event():
    # permette di comunicare con il thread di comunicazione, permette di attivare o fermare l'ascolto del robot
    if event.is_set():
        event.clear()
        button_communication_channel.config(text="Client not listening")
        salva_misura()
    else:
        event.set()
        button_communication_channel.config(text="Client listening")


def communication_channel(evento):
    button_communication_channel.config(text="Client is listening", command=setting_event)
    asyncio.run(communication_channel_async(evento))


async def communication_channel_async(evento):
    while True:
        if evento.is_set():
            await node.watch(events=True)
        else:
            await node.unwatch(events=True)
        await client.sleep(0.01)


def lock_robot():
    asyncio.run(lock_robot_async())


async def lock_robot_async():
    testo = button_main['text']
    if testo == "Robot locked":
        await node.unlock()
        button_main.config(text="Robot unlocked")
    else:
        await node.lock()
        button_main.config(text="Robot locked")


def async_main():
    asyncio.run(main())


async def collega_compila_nodo():
    global node, client
    node = await client.wait_for_node()
    nodo_libero = False
    try:
        node = await node.lock()
        nodo_libero = True
    except tdmclient.clientasync.NodeLockError:
        print("Il robot è occupato")
    if nodo_libero:
        button_main.config(text="Robot locked", command=lock_robot)
        await node.register_events(
            [("velocitaMotori", 5), ("setFrequency", 1), ("algoritmoInFunzione", 0), ("setSpeed", 1), ("reset", 0),
             ("startStop", 1)])
        error = await node.compile(aseba_program)
        print(error)
        await node.run()
    else:
        return
    return node


async def main():
    global aseba_program, client, node
    try:
        client = ClientAsync()
        client.add_event_received_listener(elaborazione_evento)
        node = await asyncio.wait_for(collega_compila_nodo(), timeout=3)
    except asyncio.TimeoutError:
        print("Operazione troppo lunga, sembra che non ci sia alcun robot")
    except ConnectionRefusedError:
        print("Devi aprire thymio suite... se no non funziona niente")
    # camera = await ...


window = tk.Tk()
window.title("Thymio Client")
window.config(bg="blue")

tabControl = ttk.Notebook(window)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text='Setting and connection thymio robot')
tabControl.add(tab2, text='Stampa dati')
tabControl.pack(expand=1, fill="both")

# ------------TAB1------------
# ------------TAB1------------
frame_sopra = tk.Frame(tab1, width=400, height=400)
frame_sopra.grid(row=0, column=0, padx=10, pady=5)

button_main = tk.Button(frame_sopra, text="Esegui collegamento", command=async_main)
button_main.grid(row=2, column=0, padx=10, pady=10)

# label_frequency = tk.Label(frame_sopra, text="Frequenza di campionamento")
# label_frequency.grid(row=0, column=0, padx=10, pady=10)

# entry_frequency = tk.Entry(frame_sopra)
# entry_frequency.grid(row=0, column=1, padx=10, pady=10)

# button_set_frequency = tk.Button(frame_sopra, text="Set frequency", command=set_frequency)
# button_set_frequency.grid(row=0, column=3, padx=10, pady=10)

label_speed = tk.Label(frame_sopra, text="Velocità base Thymio")
label_speed.grid(row=1, column=0, padx=10, pady=10)

entry_speed = tk.Entry(frame_sopra)
entry_speed.grid(row=1, column=1, padx=10, pady=10)

button_set_speed = tk.Button(frame_sopra, text="Set speed", command=set_speed)
button_set_speed.grid(row=1, column=3, padx=10, pady=10)

label_initial_condition = tk.Label(frame_sopra, text="Condizioni iniziali [X,Y,Theta]")
label_initial_condition.grid(row=0, column=0, padx=10, pady=10)

entry_initial_condition_x = tk.Entry(frame_sopra)
entry_initial_condition_x.grid(row=0, column=1, padx=10, pady=10)

entry_initial_condition_y = tk.Entry(frame_sopra)
entry_initial_condition_y.grid(row=0, column=2, padx=10, pady=10)

entry_initial_condition_phi = tk.Entry(frame_sopra)
entry_initial_condition_phi.grid(row=0, column=3, padx=10, pady=10)

button_initial_condition = tk.Button(frame_sopra, text="Set starting position", command=set_starting_position)
button_initial_condition.grid(row=0, column=4, padx=10, pady=10)

button_reset = tk.Button(frame_sopra, text="Reset variables", command=send_reset)
button_reset.grid(row=2, column=3, padx=10, pady=10)

button_stato_algoritmo = tk.Button(frame_sopra, text="Follow line OFF", command=send_change_state_algorithm)
button_stato_algoritmo.grid(row=2, column=1, padx=10, pady=10)

button_communication_channel = tk.Button(frame_sopra, text="Client not listening",
                                         command=threading.Thread(target=communication_channel, args=(event,)).start)
button_communication_channel.grid(row=2, column=2, padx=10, pady=10)

# ------------TAB2------------
# ------------TAB2------------

frame_stampa = tk.Frame(tab2, width=400, height=400)
frame_stampa.grid(row=0, column=0, padx=10, pady=5)

button_stampa = tk.Button(frame_stampa, text="Stampa", command=stampa_dati)
button_stampa.grid(row=2, column=1, padx=10, pady=10)

quale_misurazione_stampare = ttk.Combobox(frame_stampa)
quale_misurazione_stampare.grid(row=0, column=0, padx=10, pady=5)

button_numpy = tk.Button(frame_stampa, text="Stampa numpy", command=stampa_numpy)
button_numpy.grid(row=2, column=2, padx=10, pady=10)

button_odometria = tk.Button(frame_stampa, text="Stampa odometria", command=stampa_odometria)
button_odometria.grid(row=2, column=3, padx=10, pady=10)

window.mainloop()
