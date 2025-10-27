from tdmclient import ClientAsync
import numpy as np
import matplotlib.pyplot as plt

client = ClientAsync()
# abbiamo messo 2 timer per capire un po come funzionava la questione
aseba_program = """
var ciclo_100hz = 0
var p1 = 0
motor.left.target = 150
motor.right.target = 150
onevent prox
 p1 = prox.ground.delta[0]
 if p1<=500 then
  motor.left.target = 100
  motor.right.target = 100
  end

onevent motor
 ciclo_100hz = ciclo_100hz +1
 emit dati [motor.left.speed, motor.right.speed, ciclo_100hz]
"""

salva_dati = []


def on_event_received(node, event_name, event_data):
    if event_name == "start":
        print("Linea nera: " + str(event_data[0]), event_data[1])
    if event_name == "dati":
        data = [event_data[0], event_data[1], event_data[2]]
        salva_dati.append(data)


client.add_event_received_listener(
    on_event_received)  # quando il client riceve un evento allora lo fa eseguire da una funzione


def plotta():
    global salva_dati
    array = np.array(salva_dati)
    velocita_sinistra = array.T[0]
    velocita_destra = array.T[1]
    tempi = array.T[2]
    plt.plot(tempi * 0.01, velocita_sinistra)
    plt.plot(tempi * 0.01, velocita_destra)
    plt.show()


async def prog():  # da capire come funzione async e wait per bene
    node = await client.wait_for_node()
    print(node)
    error = await node.lock()
    print(error)
    error = await node.register_events(
        [("start", 2), ("dati", 3)])  # dichiariamo gli eventi che ci scambiamo
    print(error)
    error = await node.compile(aseba_program)
    print(error)
    error = await node.watch(events=True)
    print(error)
    error = await node.run()
    print(error)
    await client.sleep(17)  # lascia il client in attesa per un tempo indefinito se (),
    print("done")
    plotta()
    np.save("transitorio_150_100", salva_dati)


client.run_async_program(prog)

# c'è da capire se arrivati alla fine il client rimane in ascolto oppure tutto si chiude, non rimane in ascolto !!
