from tdmclient import ClientAsync, aw

# Questo programma illustra come inviare e ricevere eventi utilizzando la libreria 'tdmclient'.


# All'avvio del programma, il robot parte con una velocità [100, 0], il che lo fa ruotare attorno alla ruota destra.
# Dopo 4 secondi, scatta l'evento timer0 all'interno del robot: la velocità della ruota destra viene modificata e,
# contemporaneamente, viene emesso un evento chiamato 'equilibrioClient', contenente la velocità della ruota destra.
# Il computer riceve l'evento, a sua volta invia l'evento 'equilibrioNode', che il robot rileva impostando la velocità
# della ruota sinistra uguale a quella trasmessa dall'evento.


# OSS: Utilizzando 'await client.sleep(5)', il client rimarrà in ascolto per soli 5 secondi.
# Quindi, nel caso in cui si imposti 'timer.period[0] = 6000', l'evento emesso
# dal robot non verrà catturato dal computer.


# Questa logica di comunicazione è utilizzata all'interno di Thymio_GUI, ma viene implementata
# in modo leggermente diverso.
# In Thymio_GUI è stato fatto un uso esplicito della libreria asyncio, evitando così l'utilizzo della funzione 'aw'.

client = ClientAsync()

aseba_program = """
motor.left.target = 100
motor.right.target = 0
timer.period[0] = 4000
timer.period[1] = 10000
onevent timer0
 motor.right.target = 300
 emit equilibrioClient [motor.right.target]
onevent timer1
 motor.right.target = 0
 motor.left.target = 0

onevent equilibrioNode
 motor.left.target = event.args[0]
"""


def on_event_received(node, event_name, event_data):
    print(node, event_name, event_data)
    if event_name == "equilibrioClient":
        invio = event_data[0]
        aw(node.send_events({"equilibrioNode": [invio]}))


client.add_event_received_listener(
    on_event_received)  # Gli eventi ricevuti dal client vengono gestiti dalla funzione on_event_received


async def prog():
    node = await client.wait_for_node()
    print(node)
    error = await node.lock()
    print(error)
    error = await node.register_events(
        [("equilibrioClient", 1), ("equilibrioNode", 1)])
    print(error)
    error = await node.compile(aseba_program)
    print(error)
    error = await node.watch(events=True)
    print(error)
    error = await node.run()
    print(error)
    await client.sleep(5)  # lascia il client in attesa per un tempo indefinito se ()
    print("done")


client.run_async_program(prog)
