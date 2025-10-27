-Traiettoria nominale - è la traiettoria attorno a cui si è linearizzato il sistema.

-Traiettoria robot - contiene lo stato del robot durante la manovra x [m] - y[m] - angolo [rad] - ascissa curvilinea [m] - #cicli100hz

-La variabile del tempo è #ciclo100hz, se si nota un aumento della variabile di 10, significa che sono passati 0.1 secondi. -Oss: nel caso del wireless non c'è diretta corrispondenza tra il valore massimo di #ciclo100hz ed il numero di campioni raccolto. Questo è dovuto alla presenza di pacchetti persi, individuabili tramite la variaible #cicli100hz. Nel caso in cui la riga successiva ha un valore cicli100hz = cicli100hz_precedente + 20 si può concludere che un pacchetto dati è stato perso.

Gli altri due set di dati li ho inseriti per completezza, ma a mio parere sono poco utili. Infatti, con i dati presenti si può solamente quantificare la perdità di pacchetti in ricezione ( da robot a PC) e quindi non si può sapere se effettivamente le velocità in output dal controllore sono state settate al robot ( perdita di pacchetto da PC a robot).
