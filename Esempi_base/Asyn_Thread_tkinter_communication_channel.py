from tdmclient import ClientAsync
import tkinter as tk
import asyncio
import threading
import time

aseba_program = """
timer.period[0] = 300
onevent timer0
 emit ping [prox.ground.delta[0]]

onevent pong
 timer.period[0] = 0
"""

client = ClientAsync()
node = None
event = threading.Event()
stato_evento = False
print(event.is_set())


def on_event_received(node, event_name, event_data):
    print(node, event_name, event_data)


client.add_event_received_listener(on_event_received)


def setting_event():  # permette di settare il client come in ascolto oppure no
    global stato_evento, bottone_ascolto, event
    #print(threading.current_thread())
    #print(event.is_set())
    if stato_evento:
        event.clear()
        stato_evento = False
        bottone_ascolto.config(text="Non in ascolto")
    else:
        event.set()
        stato_evento = True
        bottone_ascolto.config(text="In ascolto")


def client_ascolto(
        evento):  # sto chiamando col bottone di creare un nuovo thread, tutte le funzioni che si aprono da qui apparterranno a tale thread
    # print(evento.is_set())
    # print(threading.current_thread())
    asyncio.run(ascolto(evento))


async def ascolto(evento):
    # print(evento.is_set())
    # print("Siamo arrivati ?")
    # print(evento)
    # print(threading.current_thread())
    # poi possiamo fare 2 funzioni async insieme, una per la telecamere ed una per il robot
    # comandndo la comunicazione con l'evento --> così ho un buon sincronismo !!!!!
    while True:
        if evento.is_set():
            watch = await node.watch(events=True)
        else:
            await node.unwatch(events=True)
        await client.sleep(0.1)


def prova_bottone():
    asyncio.run(prog())
    print("Ho inviato l'evento per fermare l'emissione di eventi")


async def prog():
    global node
    await node.send_events({"pong": []})


def carica_programma():
    asyncio.run(main())


async def main():
    global node
    node = await client.wait_for_node()
    await node.lock()
    await node.register_events([("ping", 1), ("pong", 0)])
    await node.compile(aseba_program)
    await node.run()


window = tk.Tk()
label = tk.Label(window, text="ciao")
label.pack()

tk.Button(window, text="Acquisto nodo robot, lock robot, compile e run programma aseba",
          command=carica_programma).pack()
tk.Button(window, text="inizializza thread ascolto",
          command=lambda: threading.Thread(target=client_ascolto, args=(event,)).start()).pack()

tk.Button(window, text="Fai qualcosa durante thread", command=prova_bottone).pack()
bottone_ascolto = tk.Button(window, text="Client non in ascolto", command=setting_event)
bottone_ascolto.pack()

window.mainloop()
