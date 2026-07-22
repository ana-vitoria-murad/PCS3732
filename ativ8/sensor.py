import pigpio
import time
import sys

TRIG_PIN = 14
ECHO_PIN = 15 

pi = pigpio.pi()
if not pi.connected:
    print("[ERRO] Falha ao conectar ao daemon pigpio. Execute 'sudo pigpiod'.")
    sys.exit()

pi.set_mode(TRIG_PIN, pigpio.OUTPUT)
pi.set_mode(ECHO_PIN, pigpio.INPUT)

pi.write(TRIG_PIN, 0)
time.sleep(0.1) 

def ler_distancia():
    """
    Envia o pulso ultrassônico e calcula a distância baseada no tempo de retorno.
    """
    pi.write(TRIG_PIN, 1)
    time.sleep(0.00001)
    pi.write(TRIG_PIN, 0)
    
    inicio_pulso = time.perf_counter()
    fim_pulso = time.perf_counter()
    timeout_inicio = time.perf_counter()
    
    while pi.read(ECHO_PIN) == 0:
        inicio_pulso = time.perf_counter()
        if inicio_pulso - timeout_inicio > 0.02:
            return -1.0
            
    while pi.read(ECHO_PIN) == 1:
        fim_pulso = time.perf_counter()
        if fim_pulso - inicio_pulso > 0.02:
            return -1.0
            
    duracao = fim_pulso - inicio_pulso
    
    distancia_cm = (duracao * 34300) / 2
    return round(distancia_cm, 2)

if __name__ == '__main__':
    LIMITE_PORTA_FECHADA_CM = 10.0 
    
    try:
        print("Iniciando leitura contínua do sensor ultrassônico...")
        while True:
            distancia = ler_distancia()
            
            if distancia < 0:
                print("[DEBUG] Falha na leitura do sensor (Timeout).")
            else:
                if distancia <= LIMITE_PORTA_FECHADA_CM:
                    status_str = f"Fechado (Distância: {distancia} cm)"
                else:
                    status_str = f"Aberto  (Distância: {distancia} cm)"
                    
                print(f"[DEBUG] Estado: {status_str}")
            
            time.sleep(3) 
            
    except KeyboardInterrupt:
        print("\n[SISTEMA] Interrompido pelo usuário.")
    finally:
        pi.write(TRIG_PIN, 0)
        pi.stop()import pigpio
import time
import sys

TRIG_PIN = 14
ECHO_PIN = 15 

pi = pigpio.pi()
if not pi.connected:
    print("[ERRO] Falha ao conectar ao daemon pigpio. Execute 'sudo pigpiod'.")
    sys.exit()

pi.set_mode(TRIG_PIN, pigpio.OUTPUT)
pi.set_mode(ECHO_PIN, pigpio.INPUT)

pi.write(TRIG_PIN, 0)
time.sleep(0.1) 

def ler_distancia():
    """
    Envia o pulso ultrassônico e calcula a distância baseada no tempo de retorno.
    """
    pi.write(TRIG_PIN, 1)
    time.sleep(0.00001)
    pi.write(TRIG_PIN, 0)
    
    inicio_pulso = time.perf_counter()
    fim_pulso = time.perf_counter()
    timeout_inicio = time.perf_counter()
    
    while pi.read(ECHO_PIN) == 0:
        inicio_pulso = time.perf_counter()
        if inicio_pulso - timeout_inicio > 0.02:
            return -1.0
            
    while pi.read(ECHO_PIN) == 1:
        fim_pulso = time.perf_counter()
        if fim_pulso - inicio_pulso > 0.02:
            return -1.0
            
    duracao = fim_pulso - inicio_pulso
    
    distancia_cm = (duracao * 34300) / 2
    return round(distancia_cm, 2)

if __name__ == '__main__':
    LIMITE_PORTA_FECHADA_CM = 10.0 
    
    try:
        print("Iniciando leitura contínua do sensor ultrassônico...")
        while True:
            distancia = ler_distancia()
            
            if distancia < 0:
                print("[DEBUG] Falha na leitura do sensor (Timeout).")
            else:
                if distancia <= LIMITE_PORTA_FECHADA_CM:
                    status_str = f"Fechado (Distância: {distancia} cm)"
                else:
                    status_str = f"Aberto  (Distância: {distancia} cm)"
                    
                print(f"[DEBUG] Estado: {status_str}")
            
            time.sleep(0.1) 
            
    except KeyboardInterrupt:
        print("\n[SISTEMA] Interrompido pelo usuário.")
    finally:
        pi.write(TRIG_PIN, 0)
        pi.stop()
