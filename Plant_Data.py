from opcua import Client
import time
import threading


class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("\nALARMA: Alarma en {} dectectada con valor {}\n".format(node, val))

    def event_notification(self, event):
        pass
        #print("Python: New event", event)


# Thread que obtiene datos y los almacena en self.heights, constantemente. DE la misma manera, ingresa constantemente
# las entradas almacenadas en self._u
class Plant(threading.Thread):
    def __init__(self, ip):
        super().__init__()
        self.client = Client(ip)
        self.objects = self.assign_object()
        self.heights = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0}
        self._u = [0, 0]
        self.sample_time = 0.001
        self.daemon = True     ## Que termine de medir cuando termine el programa (debug)
        self.event_measure = threading.Event()


    def assign_object(self):
        """Conecta el cliente y retorna el objeto donde se encuentra la planta en el servidor"""

        self.client.connect()
        return self.client.get_objects_node()

    def get_heights(self):
        """Obtiene las alturas y las almacena en un diccionario con indices h1, h2, h3, h4"""

        for i in range(1, 5):
            node = self.objects.get_child(['2:Parametros', f'2:Altura {i}'])   ## '2:Proceso_Tanques', '2:Tanques', f'2:Tanque{i}', '2:h'
            self.heights[f'h{i}'] = node.get_value() #NoneType object does not support item assig

    def get_show_heights(self):
        return [x for x in self.heights.values()]

    def suscribe_alarm(self):
        """Suscribe la alarma que esta overwrited en la clase SubHandler"""

        alarm = self.objects.get_child(['2:Proceso_Tanques', '2:Alarmas', f'2:Alarma_nivel'])
        handler = SubHandler()
        sub = self.client.create_subscription(500, handler)
        handle = sub.subscribe_events(alarm)
        time.sleep(0.1)

    def assign_valve_value(self):
        """Constantemente, asigna las variablaes almacenadas en el atributo self.u, a la planta"""

        u1 = self.objects.get_child(['2:Parametros', '2: Válvula 1'])   ## '2:Proceso_Tanques', '2:Valvulas', f'2:Valvula1', '2:u'
        u2 = self.objects.get_child(['2:Parametros', '2: Válvula 2'])   ## '2:Proceso_Tanques', '2:Valvulas', f'2:Valvula2', '2:u'
        u1.set_value(self.u[0])
        u2.set_value(self.u[1])

    @property
    def u(self):
        return self._u

    @u.setter
    def u(self, value):
        if not None in value:
            self._u = list(value)
        else:
            self._u = self._u


    def run(self):
        # self.suscribe_alarm()  // no hay alarma en simulacion
        while True:
            if sum(self.u) > 0:
                self.assign_valve_value()
                self.u = [0, 0]
            self.event_measure.set() ## Revisar esto porque no se esta cumpliendo
            self.get_heights()
            time.sleep(self.sample_time)

IP = '' # Edit
PORT = '4840'
url= 'opc.tcp://{}:{}}/freeopcua/server/'.format(IP, PORT)
plant = Plant(url)
