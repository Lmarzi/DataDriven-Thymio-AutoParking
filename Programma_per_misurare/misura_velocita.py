from tdmclient import ClientAsync
import numpy as np

client = ClientAsync()
# abbiamo messo 2 timer per capire un po come funzionava la questione
aseba_program = """
var ciclo_100hz = 0
var p1 = 0
var statoProgramma = 0
var ciclo = 0
motor.left.target = 150
motor.right.target = 150
timer.period[0] = 10000
onevent prox
statoProgramma = 1
p1 = prox.ground.delta[1]
 if p1 < 500 then
  emit start [ciclo_100hz,motor.left.speed]
 end

onevent timer0
 if ciclo == 3 then
  timer.period[1] = 30000
  end
 ciclo = ciclo + 1
 #motor.left.target = 0
 #motor.right.target = 0
 

onevent buttons 
 if button.forward ==1 then
 motor.left.target = 0
 motor.right.target = 0
 end

onevent timer1
 #motor.left.target = 0
 #motor.right.target = 0
 
onevent motor
 ciclo_100hz=ciclo_100hz+1
 emit dati [ciclo_100hz,motor.left.speed,motor.right.speed]

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
    await client.sleep(180)  # lascia il client in attesa per un tempo indefinito se (),
    print("done")
    np.save("Misura motori", salva_dati)


client.run_async_program(prog)

# c'è da capire se arrivati alla fine il client rimane in ascolto oppure tutto si chiude, non rimane in ascolto !!
