import pigpio
import time

SERVO_PIN = 18
BUZZER_PIN = 4

FREQ_A5 = 880

pi = pigpio.pi()

if not pi.connected:
    print("Erro: Não foi possível conectar ao daemon do pigpio.")
    exit()

estado = False

print("Iniciando metrônomo. Pressione Ctrl+C para sair.")

try:
    while True:
        if estado:
            pi.set_servo_pulsewidth(SERVO_PIN, 1000)
        else:
            pi.set_servo_pulsewidth(SERVO_PIN, 2000)

        pi.set_PWM_frequency(BUZZER_PIN, FREQ_A5)
        pi.set_PWM_dutycycle(BUZZER_PIN, 128)
        
        time.sleep(0.10)

        pi.set_PWM_dutycycle(BUZZER_PIN, 0)

        estado = not estado
        
        time.sleep(0.90)

except KeyboardInterrupt:
    print("\nMetrônomo interrompido pelo usuário.")

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.set_PWM_dutycycle(BUZZER_PIN, 0)
    pi.stop()
