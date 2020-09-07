from opcua import Server
import time

server = Server()

IP = '' # Edit
PORT = '4840'
url= 'opc.tcp://{}:{}}'.format(IP, PORT)
server.set_endpoint(url)

name = 'SIMULACION TANQUES'
addspace = server.register_namespace(name)

node = server.get_objects_node()

Param = node.add_object(addspace, "Parametros")

H_1 = Param.add_variable(addspace, "Altura 1", 0)
H_2 = Param.add_variable(addspace, "Altura 2", 0)
H_3 = Param.add_variable(addspace, "Altura 3", 0)
H_4 = Param.add_variable(addspace, "Altura 4", 0)
U_1 = Param.add_variable(addspace, "Válvula 1", 0)
U_2 = Param.add_variable(addspace, "Válvula 2", 0)

H_1.set_writable()
H_2.set_writable()
H_3.set_writable()
H_4.set_writable()
U_1.set_writable()
U_2.set_writable()

server.start()
print(f'Server started at {url}')

while True:

    h_1, h_2, h_3, h_4, u_1, u_2 = 5, 10, 15, 25, 0.5, -0.5
    #print(h_1, h_2, h_3, h_4, u_1, u_2)
    H_1.set_value(h_1)
    H_2.set_value(h_2)
    H_3.set_value(h_3)
    H_4.set_value(h_4)
    U_1.set_value(u_1)
    U_2.set_value(u_2)
    time.sleep(2)
