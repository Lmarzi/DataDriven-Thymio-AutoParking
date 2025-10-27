# TESI_Marzi_Lorenzo
This repo contains all the code produced in the Bachelor's thesis of Marzi Lorenzo

STORICO MODIFICHE:
 - implementare uno strumento per terminare la registrazione dati --> fatto
 - Aggiungere bottone che si occupa esclusivamente di impostare il client come 'in ascolto' oppure no --> fatto
 - Sistemare ireg proporzionale a ndev invece di preg ( in pratica non cambia niente, ma è più chiara la logica)
 - Aggiungere la possibilità di effettuare più misurazione senza spegnere ogni volta il programma, il problema sta nella logica di salvataggio dati. Bisogna scegliere in maniera corretta la costante da togliere ad ogni elemento dell'array. --> fatto
 - Aggiungere la possibilità di stampare le misurazione su file di testo diverso oppure in un unico file. --> fatto
 - Safety check che quando si preme il bottone conessione il robot sia libero, il problema è il freeze della gui --> fatto
 - Cambiare il modo in cui si prende il tempo delle misurazioni, non bisogna ragionare dal phyton pc. Deve essere il robot ad inviare il tempo con un suo timer interno, modulo clock. Soluzione: Non serve il modulo clock, coviene semplicemente scrivere una variabile sul thymio 10_hz_clock, ogni volta che si attiva l'evento prox
si fa 10_hz_clocl = 10_hz_clock + 1. Conoscendo quindi quanto volte è stato chiamato, dovremmo essere in grado di capire i secondi.  --> fatto
- Aggiungere un safety check alla variabile num_100hz, c'è un overflow a 32767 (16 bit). 32767 * (periodo) = #secondi prima di overflow. 32767 * (0,01) = 327,67 s , quindi 5 min 30 sec
- Bisogna effettuare la calibrazione dei motori, quindi controllare se la relazione tra motor.left/right.speed del robot e velocità effettiva sia lineare o meno. Dai primi test sempra che sia lineare a tratti, bisogna definire tabella con le costanti di proporzionalità. AGGIUNGERE PROCEDURA DI CALIBRAZIONE
- Odometria effettuata tramite metodi di meccanica razionale.
- Fare programma per far eseguire al robot una traiettoria analitica e poi confrontarla con quella ottenuta dall'odometria
- Implementare l'odometria in tempo reale all'interno del ciclo di raccolta dati, serve ad effettuare un eventuale controllo
- Implementare un metodo per impostare le condizioni iniziali del robot
  


OSSERVAZIONI: 
-Robot posizionato in una zona monocolore amplia, allora ireg tende a divergere e con essi anche la velocità del motori. Capire se è un problema e risolverlo, idea iniziale: se supero una certa quota ireg resettarla a 0. --> fatto
-Valori alti della costante proporzionale ho un buon comportamento in curva ma peggiore comportamento sul rettilineo, per valori bassi vale il contrario
- ATTENZIONE: sembra che il sensore prox.ground.x[1] non funzioni benissimo. Lavora in un range [0,500] invece di [0,1024]
- La variabile client.DEFAULT_SLEEP indica tutti gli time step per eseguire le operazioni. Esempi: Buffer di ricezione eventi viene controllato ad ogni time step, l'invio di eventi viene effettuato ad ogni time step.
- La connessione wireless perde di stabilità nel momento in cui il robot deve sia riceve che inviare eventi ad alte frequenze. 


LINK IMPORTANTI:
https://mobsya.github.io/aseba/index.html#
https://stephane.magnenat.net/publications/Seamless%20Multi-Robot%20Programming%20for%20the%20People,%20Aseba%20and%20the%20Wireless%20Thymio%20II%20Robot%20-%20R%C3%A9tornaz%20et%20al.%20-%20ICIA%20-%202013.pdf    #WIRELESS THYMIO ii


LINK TELECAMERA:
- drivers disponibili nvidia https://www.nvidia.com/download/find.aspx#
- cuda compatibility con i drivers grafici https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html#cuda-major-component-versions__table-cuda-toolkit-driver-versions
- specifiche per l'installazione https://www.stereolabs.com/docs/installation/specifications/
- computetional power https://developer.nvidia.com/cuda-gpus#compute
