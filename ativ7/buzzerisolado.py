import pigpio
from time import sleep

BUZZER_PIN = 12

pi = pigpio.pi()

if not pi.connected:
    print("Erro: Não foi possível conectar ao daemon do pigpio.")
    exit()

FREQ_A4 = 440

VOLUME = 500000 

try:
    while True:
        pi.hardware_PWM(BUZZER_PIN, FREQ_A4, VOLUME)
        sleep(1)

        pi.hardware_PWM(BUZZER_PIN, 0, 0)
        sleep(1)

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário.")

finally:
    pi.hardware_PWM(BUZZER_PIN, 0, 0)
    pi.stop()
