import pigpio
from time import sleep

SERVO_PIN = 18

pi = pigpio.pi()

if not pi.connected:
    print("Erro: Não foi possível conectar ao daemon do pigpio.")
    exit()

try:
    while True:
        pi.set_servo_pulsewidth(SERVO_PIN, 500)
        sleep(2)

        pi.set_servo_pulsewidth(SERVO_PIN, 1000)
        sleep(2)

        pi.set_servo_pulsewidth(SERVO_PIN, 1500)
        sleep(2)

        pi.set_servo_pulsewidth(SERVO_PIN, 2000)
        sleep(2)

        pi.set_servo_pulsewidth(SERVO_PIN, 2500)
        sleep(2)

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário.")

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()
