import pigpio
import time
import sys

pi = pigpio.pi()
if not pi.connected:
    print("[ERRO] Falha ao conectar ao daemon pigpio. Execute 'sudo pigpiod'.")
    sys.exit()
[16, 20, 21, 26]
LINHAS =  [16, 20, 21, 26] # checar os pinos
COLUNAS = [19, 13, 6, 5] # checar os pinos
MATRIZ = [
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']
]

for col in COLUNAS:
    pi.set_mode(col, pigpio.OUTPUT)
    pi.write(col, 1) 

for lin in LINHAS:
    pi.set_mode(lin, pigpio.INPUT)
    pi.set_pull_up_down(lin, pigpio.PUD_UP)
    pi.set_glitch_filter(lin, 50000) 

tecla_anterior = None 

def ler_teclado():
    global tecla_anterior
    tecla_atual = None
    
    for j in range(4):
        pi.write(COLUNAS[j], 0) 
        for i in range(4):
            if pi.read(LINHAS[i]) == 0: 
                tecla_atual = MATRIZ[i][j]
        pi.write(COLUNAS[j], 1) 
        
        if tecla_atual:
            break 
            
    if tecla_atual != tecla_anterior:
        tecla_anterior = tecla_atual
        return tecla_atual
        
    return None

if __name__ == '__main__':
    try:
        print("[SISTEMA] Aguardando entrada do teclado...")
        while True:
            tecla = ler_teclado()
            if tecla:
                print(f"[DEBUG] Tecla pressionada: {tecla}")
                
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n[SISTEMA] Interrompido pelo usuário.")
    finally:
        for col in COLUNAS:
            pi.write(col, 1) 
        pi.stop() 
