from tdmclient import ClientAsync

# programma scritto nel linguaggio comprensibile dal robot
aseba_program = """
var tempo_16hz = 0
var speed = 30
var tempo_1hz = 0
onevent temperature
tempo_1hz++
motor.right.target = speed*tempo_1hz
motor.left.target=speed*tempo_1hz
onevent acc
tempo_16hz++
emit odometria [acc[1],tempo_16hz,motor.right.speed,motor.left.speed]
"""

client = ClientAsync()

dati_odometria = []


# funzione per elaborare gli eventi ricevuti
def on_event_received(node, event_name, event_data):
    print(node, event_name, event_data)
    if event_name == "odometria":
        dati_odometrici = [event_data[0], event_data[1]]
        velocita_motori = [event_data[2], event_data[3]]  # left - right
        dati = [dati_odometrici, velocita_motori]
        dati_odometria.append(dati)


# quando arriva un evento dal robot al client allora inerviene la funzione on_event_received
client.add_event_received_listener(on_event_received)


async def array_velocita_tempo(array):
    array_ritorno = []
    for item in array:
        array_ritorno.append(item[1])
    return array_ritorno


async def calcoli_velocita(array):
    array_ritorno = []
    velocita_k = 0  # sarebbe velocità iniziale
    for item in array:
        velocita_k = velocita_k + item[0][0] * item[0][1]
        array_ritorno.append([velocita_k, item[0][1]])
    return array_ritorno


async def prog():
    global dati_odometria
    node = await client.wait_for_node()
    await node.lock()
    await node.register_events([("odometria", 4)])  # bisogna definire l'evento personalizzato al robot
    error = await node.compile(aseba_program)  # compilazione del programma aseba
    print(error)
    await node.watch(events=True)  # attivazione eventi
    await node.run()
    await client.sleep(4)  # il client rimane in ascolto per tot secondi
    array_velocita = await array_velocita_tempo(dati_odometria)
    array_velocita_misurate = await calcoli_velocita(dati_odometria)
    #print("CONFRONTIAMO GLI ARRAY")
    #print(array_velocita)
    #print(array_velocita_misurate)
    print("done")
    print(dati_odometria)
    print(len(dati_odometria))


client.run_async_program(prog)
