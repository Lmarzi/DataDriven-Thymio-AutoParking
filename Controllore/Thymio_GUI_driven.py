import matplotlib.pyplot as plt
import tdmclient.clientasync
from tdmclient import ClientAsync
import tkinter as tk
from tkinter import ttk
import asyncio
import threading
import numpy as np
import odometria_real_time as odr
import implementazione_data_driven as data_driven
import time

aseba_program = """
var ciclo_100hz = 0
var statoProgramma = 0
onevent motor
 if statoProgramma == 1 then
 ciclo_100hz = ciclo_100hz +1
 end

onevent prox
if statoProgramma == 1 then
emit velocitaMotori [motor.left.speed, motor.right.speed , ciclo_100hz]
end
#onevent buttons
# if statoProgramma == 1 then
# emit velocitaMotori [motor.left.speed, motor.right.speed , ciclo_100hz]
# end

onevent velocitaControllore
 motor.left.target = event.args[0]
 motor.right.target = event.args[1]

onevent startStop
 if statoProgramma == 1 then
   statoProgramma = 0
 else
   statoProgramma = 1
 end
 motor.left.target = 0
 motor.right.target = 0
 ciclo_100hz = 0

"""
# ---- DEFINIZIONI VARIABILI E COSTANTI -----
global node, client
U_nom = data_driven.U_nom
X_nom = data_driven.X_nom
matrice_K = data_driven.K  # matrice controllore
v_fil = np.zeros(2)
T_fil = data_driven.T_fil  # costante di tempo del filtro passa-basso
n = data_driven.n
# tau = (n * 0.01) / n
tau = data_driven.tau
posizione = [data_driven.x_0[0], data_driven.x_0[1], data_driven.x_0[2], 0, 0]
dati_odometria = [posizione]
velocita_inviate_fisiche = []
velocita_inviate_robot = []
velocita_attuali_robot = []
v_rob = [0, 0]  # velocità da inviare al robot
step = 0
quanto_sottocampiono = data_driven.tempo_da_100hz_a_sotto_campionamento
tempo_intervallo_campionamento = quanto_sottocampiono * 0.01
event = threading.Event()  # permette di interagire con il thread di comunicazione
event.set()
stato_ascolto = False
primo_ciclo = True
secondo_ciclo = True

# def invio_dati(vel):
#    asyncio.run(async_invio_dati(vel))


# async def async_invio_dati(vel):
#    v = {"motor.left.target": [vel[0]], "motor.right.target": [vel[1]]}
#    await node.set_variables(v)


# svuota_buffer = 10

tempo_precedente = 0
pacchetti_persi = 0


def elaborazione_evento(nodo, nome_evento, data_evento):
    global posizione, v_fil, v_rob, step, dati_odometria, velocita_inviate_robot, velocita_inviate_fisiche, \
        velocita_attuali_robot, secondo_ciclo, tempo_precedente, pacchetti_persi, primo_ciclo
    # aggiunto event.is_set() per evitare di raccogliere dati nel tempo che ci mette al client di uscire dall'ascolto

    if nome_evento == "velocitaMotori" and (step < n - 1) and not (primo_ciclo):
        step += 1
        print(nome_evento, data_evento)
        if tempo_precedente != data_evento[2] - quanto_sottocampiono:
            pacchetti_persi += 1
            if tempo_precedente <= data_evento[2] - 2 * quanto_sottocampiono:
                pacchetti_persi += 1
        tempo_precedente = data_evento[2]
        # print(step)
        # print("Ricevuto", time.perf_counter())
        if secondo_ciclo:
            dati_odometria[0][4] = data_evento[2] - 1
            secondo_ciclo = False
        velocita_motori = [data_evento[0], data_evento[1], data_evento[2]]
        velocita_attuali_robot.append([data_evento[0], data_evento[1], data_evento[2]])
        posizione = odr.posizione_nuova(velocita_motori, posizione)
        dati_odometria.append(posizione)
        x_reg = np.array([posizione[0], posizione[1], posizione[2]])
        u = U_nom[step]  # in m/s
        vel = u + np.dot(matrice_K[step], (x_reg - X_nom[step]))
        v_fil = v_fil + tau * (vel - v_fil) / T_fil
        velocita_inviate_fisiche.append(v_fil)
        invio_dati = data_driven.mezzeria_angolare_to_velocita_motori(v_fil[0], v_fil[1])
        v_rob = [odr.velocita_robot(invio_dati[0]),
                 odr.velocita_robot(invio_dati[1])]
        # threading.Thread(target=invio_dati, args=v_rob).start()
        if step == (n - 1):
            v_rob = [0, 0]
            print("SOno stati persi ", pacchetti_persi - 1, " pacchetti su ", step, " pacchetti ricevuti")
            print("FINITO INSEGUIMENTO")
        # Serve ad evitare il problema del controllore nei campioni finali,
        # bisogna aggiornare il numero traiettoria per traiettoria
        if step >= n - 1:
            v_rob = [0, 0]
            event.clear()
            button_communication_channel.config(text="Avvio controllore")
    # svuota_buffer -= 1
    # print("Siamo quo")
    primo_ciclo = False


def setting_event():
    # permette di avvitare o disattivare l'ascolto attivo degli eventi provinienti dal robot
    if event.is_set():
        event.clear()
        button_communication_channel.config(text="Avvio controllore")
    else:
        event.set()
        button_communication_channel.config(text="Controllore avviato")


async def async_send_motor_target(v_robot):
    await node.send_events({"velocitaControllore": [v_robot[0], v_robot[1]]})


async def async_send_stop():
    await node.send_events({"startStop": []})


def set_starting_position():
    global dati_odometria, posizione
    x = float(entry_initial_condition_x.get())
    y = float(entry_initial_condition_y.get())
    phi = float(entry_initial_condition_phi.get())
    posizione = [x, y, phi, 0, 0]
    dati_odometria = [posizione]


def communication_channel(evento):
    button_communication_channel.config(text="Controllore avviato", command=setting_event)
    asyncio.run(communication_channel_async(evento))


async def communication_channel_async(evento):
    global v_rob, step, posizione, stato_ascolto, velocita_inviate_robot
    # i = 0
    while True:
        # print("Siamo  alla numero ", i)
        # print(evento.is_set() == True, ascolto == False)
        # time.sleep(1)
        if evento.is_set():
            if not stato_ascolto:
                await node.watch(events=True)
                await async_send_stop()
                stato_ascolto = True
            else:
                v_rob_2 = v_rob
                v = {"motor.left.target": [v_rob_2[0]], "motor.right.target": [v_rob_2[1]]}
                velocita_inviate_robot.append(v_rob_2)
                await node.set_variables(v)
                print("Inviato", v_rob, time.perf_counter())
                # await async_send_motor_target(v_rob)
        else:
            if stato_ascolto:
                step = 0
                await node.unwatch(events=True)
                await async_send_stop()
                stato_ascolto = False
            else:
                time.sleep(1)
        # if (evento.is_set() == True) and (ascolto == False):
        #   await node.watch(events=True)
        #  await async_send_stop()
        # ascolto = True
        # print(evento.is_set() == False, ascolto == True)
        # if (evento.is_set() == False) and (ascolto == True):
        #   step = 0
        #  await node.unwatch(events=True)
        # await async_send_stop()
        # ascolto = False
        # print(evento.is_set() == True, ascolto ==  True)
        # if (evento.is_set() == True) and (ascolto == True):
        #   await async_send_motor_target(v_rob)
        # print(evento.is_set and True, ascolto)
        # time.sleep(5)
        # i = i +
        # if (evento.is_set() == False) and (ascolto == False):
        #   time.sleep(2)


def grafici_salva_dati():
    global dati_odometria, posizione, velocita_inviate_robot, velocita_inviate_fisiche, velocita_attuali_robot, primo_ciclo
    dati_odometria = np.array(dati_odometria)
    velocita_inviate_fisiche = np.array(velocita_inviate_fisiche)
    velocita_inviate_rt = np.array(velocita_inviate_robot)
    velocita_inviate_rt = velocita_inviate_rt[1:len(velocita_inviate_rt), :]
    velocita_attuali_rt = np.array(velocita_attuali_robot)
    nome_cartella = data_driven.crea_cartella("dati_controllo_robot")
    plt.clf()
    # --- PLOT DELLA TRAIETTORIA ESEGUITA IN M ---
    plt.title("Traiettorie [m] ")
    plt.plot(dati_odometria.T[0] * 100, dati_odometria.T[1] * 100, label="Traiettoria robot")
    plt.plot(X_nom.T[0] * 100, X_nom.T[1] * 100, label="Traiettoria nominale")
    plt.grid()
    plt.legend()
    data_driven.salva_dati(dati_odometria, nome_cartella, "traiettoria_robot",
                           ["x", "y", "angolo", "ascissa curvilinea", "# cicli 100hz"])
    data_driven.salva_dati(X_nom, nome_cartella, "traiettoria_nominale", ["x", "y", "angolo"])
    # --- PLOT DELLE VELOCITA PER IL MODELLO UNICICLO cm/s e gradi/s ---
    # fig, ax1 = plt.subplots()
    # color = 'tab:red'
    # ax1.set_xlabel('time (s)')
    # ax1.set_ylabel('velocita lineare mezzeria cm/s', color=color)
    # ax1.plot(t, velocita_inviate_fisiche.T[0] * 100, color=color)
    # ax1.tick_params(axis='y', labelcolor=color)
    # ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    # color = 'tab:blue'
    # ax2.set_ylabel('velocita angolare gradi/s', color=color)  # we already handled the x-label with ax1
    # ax2.plot(t, velocita_inviate_fisiche.T[1] * 360 / 3.1415, color=color)
    # ax2.tick_params(axis='y', labelcolor=color)
    # fig.tight_layout()
    # plt.grid()
    # --- PLOT DELL'ANGOLO DEL ROBOT MISURATO VS NOMINALE ---
    plt.figure("Angolo robot")
    plt.plot(np.linspace(0, len(X_nom.T[2]) * tempo_intervallo_campionamento, len(X_nom.T[2])),
             X_nom.T[2] * 180 / 3.1415,
             label="Angolo nominale")
    plt.plot(np.linspace(0, len(dati_odometria.T[2]) * tempo_intervallo_campionamento, len(dati_odometria.T[2])),
             dati_odometria.T[2] * 180 / 3.1415,
             label="Angolo robot")
    plt.grid()
    plt.legend()
    # --- PLOT DI VELOCITA ROBOT SINISTRA MISURATA VS CONTROLLORE ---
    plt.figure("Velocita robot sinistra")
    plt.plot(np.linspace(client.DEFAULT_SLEEP, len(velocita_inviate_rt.T[0]) * client.DEFAULT_SLEEP,
                         len(velocita_inviate_rt.T[1])),
             velocita_inviate_rt.T[0], label="Motore sinistro controllore", drawstyle="steps-post")
    plt.plot(
        np.linspace(0, (len(velocita_attuali_rt.T[0]) - 1) * tempo_intervallo_campionamento,
                    len(velocita_attuali_rt.T[1])),
        velocita_attuali_rt.T[0], label="Motore sinistro attuale",drawstyle="steps-post")
    plt.grid()
    plt.legend()
    # --- PLOT DI VELOCITA ROBOT DESTRA MISURATA VS CONTROLLORE ---
    plt.figure("Velocita robot destra")
    plt.plot(np.linspace(client.DEFAULT_SLEEP, len(velocita_inviate_rt.T[1]) * client.DEFAULT_SLEEP,
                         len(velocita_inviate_rt.T[1])),
             velocita_inviate_rt.T[1], label="Motore destro controllore", drawstyle="steps-post")
    plt.plot(
        np.linspace(0, (len(velocita_attuali_rt.T[1]) - 1) * tempo_intervallo_campionamento,
                    len(velocita_attuali_rt.T[1])),
        velocita_attuali_rt.T[1], label="Motore destro attuale")
    plt.grid()
    plt.legend()
    data_driven.salva_dati(velocita_inviate_rt, nome_cartella, "velocita_inviate_da_controllore",
                           ["motor.left.target", "motor.right.target"])
    data_driven.salva_dati(velocita_attuali_rt, nome_cartella, "velocita_attuali_robot",
                           ["motor.left.target", "motor.right.target", "#cicli 100hz"])
    plt.show()
    # --- RIPRISTINO ALLE CONDIZIONI INIZIALI ---
    velocita_inviate_robot = []
    velocita_attuali_robot = []
    velocita_inviate_fisiche = []
    posizione = [dati_odometria[0][0], dati_odometria[0][1], dati_odometria[0][2], dati_odometria[0][3],
                 dati_odometria[0][4]]
    dati_odometria = [posizione]
    primo_ciclo = True


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
            [("velocitaMotori", 3),
             ("startStop", 0), ("velocitaControllore", 2), ("reset", 0)])
        error = await node.compile(aseba_program)
        print(error)
        await node.run()
    else:
        return
    return node


async def main():
    global client, node
    try:
        client = ClientAsync()
        client.DEFAULT_SLEEP = 0.1
        client.add_event_received_listener(elaborazione_evento)
        node = await asyncio.wait_for(collega_compila_nodo(), timeout=3)
    except asyncio.TimeoutError:
        print("Operazione troppo lunga, sembra che non ci sia alcun robot")
    except ConnectionRefusedError:
        print("Devi aprire thymio suite... se no non funziona niente")
    # camera = await ...


window = tk.Tk()
window.title("Thymio DATA DRIVEN control")
window.config(bg="blue")

tabControl = ttk.Notebook(window)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text='')
tabControl.pack(expand=1, fill="both")

# ------------TAB1------------
# ------------TAB1------------
frame_sopra = tk.Frame(tab1, width=400, height=400)
frame_sopra.grid(row=0, column=0, padx=10, pady=5)

button_main = tk.Button(frame_sopra, text="Esegui collegamento", command=async_main)
button_main.grid(row=2, column=0, padx=10, pady=10)

button_communication_channel = tk.Button(frame_sopra, text="Avvio controllore",
                                         command=threading.Thread(target=communication_channel, args=(event,)).start)
button_communication_channel.grid(row=2, column=2, padx=10, pady=10)

button_plot = tk.Button(frame_sopra, text="Traiettoria ultima misura", command=grafici_salva_dati)
button_plot.grid(row=3, column=0, padx=10, pady=10)

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

window.mainloop()

