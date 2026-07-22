import pigpio
import time
import sys

BUZZER_PIN = 12 # checar o pino

pi = pigpio.pi()
if not pi.connected:
    print("[ERRO] Falha ao conectar ao daemon pigpio. Execute 'sudo pigpiod'.")
    sys.exit()

pi.set_mode(BUZZER_PIN, pigpio.OUTPUT)
pi.write(BUZZER_PIN, 0) 

buzzer_ligado = False
tempo_inicio_buzzer = 0
duracao_buzzer = 0

def acionar_buzzer(duracao_segundos):
    global buzzer_ligado, tempo_inicio_buzzer, duracao_buzzer
    pi.write(BUZZER_PIN, 1) 
    buzzer_ligado = True
    tempo_inicio_buzzer = time.time()
    duracao_buzzer = duracao_segundos

def atualizar_buzzer():
    global buzzer_ligado
    if buzzer_ligado:
        if (time.time() - tempo_inicio_buzzer) >= duracao_buzzer:
            pi.write(BUZZER_PIN, 0) 
            buzzer_ligado = False

if __name__ == '__main__':
    try:
        print("[DEBUG] Evento: Senha Correta - Bipe Curto")
        acionar_buzzer(0.2) 
        
        while True:
            atualizar_buzzer()

            if not buzzer_ligado:
                print("[DEBUG] Temporização concluída.")
                break
                
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
    finally:
        pi.write(BUZZER_PIN, 0) 
        pi.stop()
