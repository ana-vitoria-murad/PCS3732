import pigpio
import time

SERVO_PIN = 18
BUZZER_PIN = 4
LED_PIN = 17

FREQ_A5 = 880

pi = pigpio.pi()

if not pi.connected:
    print("Erro: Não foi possível conectar ao daemon do pigpio.")
    exit()

pi.set_mode(LED_PIN, pigpio.OUTPUT)
estado = False

print("Iniciando metrônomo a 1 Hz (60 BPM). Pressione Ctrl+C para sair.")

try:
    while True:
        inicio_laco = time.time() 

        if estado:
            pi.set_servo_pulsewidth(SERVO_PIN, 1000)
        else:
            pi.set_servo_pulsewidth(SERVO_PIN, 2000)

        pi.set_PWM_frequency(BUZZER_PIN, FREQ_A5)
        pi.set_PWM_dutycycle(BUZZER_PIN, 128)
        pi.write(LED_PIN, 1)

        time.sleep(0.10)

        pi.set_PWM_dutycycle(BUZZER_PIN, 0)
        pi.write(LED_PIN, 0)

        estado = not estado

        tempo_decorrido = time.time() - inicio_laco
        tempo_restante = 1.0 - tempo_decorrido
        
        if tempo_restante > 0:
            time.sleep(tempo_restante)

except KeyboardInterrupt:
    print("\nMetrônomo interrompido pelo usuário.")

finally:
    # Desliga os componentes de forma segura
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.set_PWM_dutycycle(BUZZER_PIN, 0)
    pi.write(LED_PIN, 0)
    pi.stop()
    print("Recursos liberados.")
