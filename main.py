import Controlador as pid
import Plant_Data as tank
#import Frontend_v6 as UI


if __name__ == '__main__':
    tank.plant.start()

    pid.control.set_controller_gain(Kp=3, Ki=30, Kd=0, ind='1')
    pid.control.set_controller_gain(Kp=2.7, Ki=40, Kd=1, ind='2')
    pid.control.plant = tank.plant

    while True:
        print('Alturas en plant son:', pid.control.get_measure())
