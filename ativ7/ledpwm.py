import pigpio
from time import sleep

LED_PIN = 18

pi = pigpio.pi()

if not pi.connected:
    print("Erro: Não foi possível conectar ao daemon do pigpio.")
    exit()

try:
    print("1 Hz")
    pi.hardware_PWM(LED_PIN, 1, 500000) 
    sleep(4)

    print("10 Hz")
    pi.hardware_PWM(LED_PIN, 10, 500000) 
    sleep(4)

    print("100 Hz")
    pi.hardware_PWM(LED_PIN, 100, 250000) 
    sleep(3)
    
    pi.hardware_PWM(LED_PIN, 100, 1000000)
    sleep(3)

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário.")

finally:
    print("Desligando LED")
    pi.hardware_PWM(LED_PIN, 0, 0)
    pi.stop()
