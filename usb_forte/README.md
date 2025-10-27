-Traiettoria nominale - è la traiettoria attorno a cui si è linearizzato il sistema.

-Traiettoria robot - contiene lo stato del robot durante la manovra x [m] - y[m] - angolo [rad] - ascissa curvilinea [m] - #cicli100hz

-La variabile del tempo è #ciclo100hz, se si nota un aumento della variabile di 10, significa che sono passati 0.1 secondi.


velocità_attuali_robot : velocità del motor sinistro e motore destro espresse adimensionalmente. (in realtà la misura è legata alla tensione ai capi del motore in DC)
velocità_inviate_da_controllore : velocità d'uscita dal controllore
