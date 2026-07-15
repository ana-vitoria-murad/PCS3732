import pigpio
import time

SERVO_PIN = 18
BUZZER_PIN = 4
LED_PIN = 17

BTN_MAIS_10 = 26
BTN_MENOS_10 = 20
BTN_MAIS_1 = 16
BTN_MENOS_1 = 21

FREQ_A5 = 880

pi = pigpio.pi()

if not pi.connected:
    print("Erro: Não foi possível conectar ao daemon do pigpio.")
    exit()

pi.set_mode(LED_PIN, pigpio.OUTPUT)

bpm = 60.0

def altera_bpm(gpio, level, tick):
    global bpm
    
    if gpio == BTN_MAIS_10:
        bpm += 10
    elif gpio == BTN_MENOS_10:
        bpm -= 10
    elif gpio == BTN_MAIS_1:
        bpm += 1
    elif gpio == BTN_MENOS_1:
        bpm -= 1
        
    if bpm < 30: 
        bpm = 30
    if bpm > 300: 
        bpm = 300
        
    print(f"Nova frequência: {bpm} BPM")

botoes = [BTN_MAIS_10, BTN_MENOS_10, BTN_MAIS_1, BTN_MENOS_1]

for btn in botoes:
    pi.set_mode(btn, pigpio.INPUT)
    pi.set_pull_up_down(btn, pigpio.PUD_UP)

    pi.set_glitch_filter(btn, 200000)

    pi.callback(btn, pigpio.FALLING_EDGE, altera_bpm)

estado = False
print(f"Metrônomo iniciado a {bpm} BPM. Pressione Ctrl+C para sair.")

try:
    while True:
        t_inicio = time.time()

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

        tempo_ciclo = 60.0 / bpm
        
        t_atual = time.time()
        tempo_execucao_do_laco = t_atual - t_inicio
        
        drift_time = tempo_ciclo - tempo_execucao_do_laco
        
        if drift_time > 0:
            time.sleep(drift_time)

except KeyboardInterrupt:
    print("\nMetrônomo interrompido pelo usuário.")

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.set_PWM_dutycycle(BUZZER_PIN, 0)
    pi.write(LED_PIN, 0)
    
    for btn in botoes:
        pi.set_glitch_filter(btn, 0)
        
    pi.stop()
