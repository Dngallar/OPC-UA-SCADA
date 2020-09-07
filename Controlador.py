from opcua import Client, ua
from opcua.ua import ua_binary as uabin
from opcua.common.methods import call_method
import time
import threading
from PID import PID


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


class Plant(threading.Thread):
    def __init__(self, ip):
        super().__init__()
        self.client = Client(ip)
        self.objects = self.assign_object()
        self.heights = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0}
        self.voltages = {'u1': 0, 'u2': 0}
        self._u = [0, 0]
        self.sample_time = 0.001
        self.daemon = True     ## Que termine de medir cuando termine el programa (debug)
        self.event_measure = threading.Event()

    def assign_object(self):
        self.client.connect()
        return self.client.get_objects_node()

    def get_valve_value(self):
        for i in range(1, 3):
            node = self.objects.get_child(['2:Proceso_Tanques', '2:Valvulas', f'2:Valvula{i}', '2:u'])
            self.voltages[f'u{i}'] = node.get_value() #NoneType object does not support item assig

    def get_heights(self):
        for i in range(1, 5):
            node = self.objects.get_child(['2:Proceso_Tanques', '2:Tanques', f'2:Tanque{i}', '2:h'])
            self.heights[f'h{i}'] = node.get_value() #NoneType object does not support item assig

    def suscribe_alarm(self):
        alarm = self.objects.get_child(['2:Proceso_Tanques', '2:Alarmas', f'2:Alarma_nivel'])
        handler = SubHandler()
        sub = self.client.create_subscription(500, handler)
        handle = sub.subscribe_events(alarm)
        time.sleep(0.1)

    def assign_valve_value(self):
        u1 = self.objects.get_child(['2:Proceso_Tanques', '2:Valvulas', f'2:Valvula1', '2:u'])
        u2 = self.objects.get_child(['2:Proceso_Tanques', '2:Valvulas', f'2:Valvula2', '2:u'])
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
        self.suscribe_alarm()
        while True:
            if sum(self.u) > 0:
                self.assign_valve_value()
                self.u = [0, 0]
            self.event_measure.set() ## Revisar esto porque no se esta cumpliendo
            self.get_heights()
            time.sleep(self.sample_time)


class Controller(threading.Thread):
    def __init__(self):
        super().__init__()
        self.plant = Plant("opc.tcp://192.168.1.23:4840")
        self.plant.start()
        self.pid_valv1 = PID()
        self.pid_valv2 = PID()
        self.is_running = False
        self.u = [0, 0]

    def get_measure(self):
        return self.plant.heights


    def convert_input(self, u, ind_valv, h_dict):
        if ind_valv == '1':
            return u / self.pid_valv1.update(h_dict['h1'], max_val=True)
        if ind_valv == '2':
            return u / self.pid_valv2.update(h_dict['h2'], max_val=True)


    def set_input(self, u1, u2):
        self.plant.u = (u1, u2)
        # print(f'Estoy recibiendo {u1} {u2}')

    def set_SetPoint(self, s1, s2):
        self.pid_valv1.SetPoint = s1
        self.pid_valv2.SetPoint = s2

    def set_controller_gain(self, Kp=float(), Ki=float(), Kd=float(), ind='1'):
        if ind == '1':
            self.pid_valv1.set_K(Kp, Ki, Kd)
        if ind == '2':
            self.pid_valv2.set_K(Kp, Ki, Kd)

    def loop(self):
        h_dict = self.get_measure()
        self.u[0] = self.convert_input(self.pid_valv1.update(h_dict['h1']), '1', h_dict)
        self.u[1] = self.convert_input(self.pid_valv2.update(h_dict['h2']), '2', h_dict)
        # print(f'Estoy enviando: {self.u}', end='')

    def stop(self):
        self.is_running = False


    def run(self):
        self.is_running = True
        self.pid_valv1.sample_time = self.plant.sample_time
        self.pid_valv2.sample_time = self.plant.sample_time
        while self.is_running:
            if self.plant.event_measure.wait():
                self.loop()
                self.set_input(self.u[0], self.u[1])
                self.plant.event_measure.clear()


if __name__ == '__main__':

    control = Controller()
    # Ks = input('Ingrese constantes: ').split(',')
    control.set_controller_gain(Kp=3, Ki=30, Kd=0, ind='1')
    control.set_controller_gain(Kp=2.7, Ki=40, Kd=1, ind='2')
    control.set_SetPoint(12, 12)

    while True:

        print('\n[1] Control PID\n[2] Manual')
        operating_op = input('Select operation mode: ')

        if operating_op == '1':
            control.start()
            while True:
                print('\n[1] Ver alturas\n[2] Ingresar set_point\n[3] Salir')
                op = input("Ingrese una opcion: ")

                if op == '1':
                    print('\nLas alturas son h: {}'.format(control.get_measure()))

                if op == '2':
                    s1, s2 = input('\nIngrese setpoint separado por comas: ').split(',')
                    control.set_SetPoint(float(s1), float(s2))

                if op == '3':
                    control.stop()
                    break

        if operating_op == '2':
            while True:
                print('\n[1] Ver alturas\n[2] Ingresar entradas\n[3] Salir')
                op = input("Ingrese una opcion: ")

                if op == '1':
                    print('\nLas alturas son h: {}'.format(control.get_measure()))

                if op == '2':
                    u1, u2 = input('\nIngrese entradas separadas por comas: ').split(',')
                    control.set_input(float(u1), float(u2))

                if op == '3':
                    break
