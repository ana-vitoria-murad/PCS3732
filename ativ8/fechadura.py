import pigpio
import time
import hashlib
import sys

pi = pigpio.pi()
if not pi.connected:
    print("[ERRO] Falha ao conectar ao daemon pigpio. Execute 'sudo pigpiod'.")
    sys.exit()

TRIG_PIN = 14 
ECHO_PIN = 15 
pi.set_mode(TRIG_PIN, pigpio.OUTPUT)
pi.set_mode(ECHO_PIN, pigpio.INPUT)
pi.write(TRIG_PIN, 0) 

BUZZER_PIN = 12
pi.set_mode(BUZZER_PIN, pigpio.OUTPUT)
pi.write(BUZZER_PIN, 0) 

LINHAS =  [26, 21, 20, 16] 
COLUNAS = [5, 6, 13, 19] 
MATRIZ = [
    ['1', '4', '7', '*'],
    ['2', '5', '8', '0'],
    ['3', '6', '9', '#'],
    ['A', 'B', 'C', 'D']
]

for col in COLUNAS:
    pi.set_mode(col, pigpio.OUTPUT)
    pi.write(col, 1) 

for lin in LINHAS:
    pi.set_mode(lin, pigpio.INPUT)
    pi.set_pull_up_down(lin, pigpio.PUD_UP)
    pi.set_glitch_filter(lin, 50000) 

# Display LCD 
I2C_BUS = 1
ENDERECO_LCD = 0x27

LCD_BACKLIGHT = 0x08
LCD_ENABLE    = 0x04
LCD_RS        = 0x01

try:
    lcd_handle = pi.i2c_open(I2C_BUS, ENDERECO_LCD)
except Exception as e:
    print(f"[ERRO] Falha ao iniciar barramento I2C via pigpio: {e}")
    lcd_handle = None

buzzer_ligado = False
tempo_inicio_buzzer = 0
duracao_buzzer = 0

tecla_anterior = None 

SENHA_CORRETA_HASH = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
buffer_senha = ""
falhas_consecutivas = 0
LIMITE_PORTA_FECHADA_CM = 10.0 
sistema_destravado = False 

def lcd_toggle_enable(bits):
    """Gera o pulso de Enable para o LCD"""
    if lcd_handle is None: return
    pi.i2c_write_byte(lcd_handle, (bits | LCD_ENABLE))
    time.sleep(0.0005)
    pi.i2c_write_byte(lcd_handle, (bits & ~LCD_ENABLE))
    time.sleep(0.0001)

def lcd_byte(bits, modo):
    """Envia byte dividindo em 2 nibbles de 4 bits"""
    if lcd_handle is None: return
    bits_high = modo | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low  = modo | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    pi.i2c_write_byte(lcd_handle, bits_high)
    lcd_toggle_enable(bits_high)
    pi.i2c_write_byte(lcd_handle, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_init():
    """Inicialização física do LCD modo 4 bits"""
    if lcd_handle is None: return
    time.sleep(0.05)
    lcd_byte(0x33, 0)
    lcd_byte(0x32, 0)
    lcd_byte(0x06, 0)
    lcd_byte(0x0C, 0)
    lcd_byte(0x28, 0)
    lcd_byte(0x01, 0) 
    time.sleep(0.005)

def atualizar_lcd(linha1, linha2=""):
    """Escreve a mensagem no terminal e envia para o LCD físico"""
    print(f"[LCD] L1: {linha1} | L2: {linha2}")
    if lcd_handle is None: return

    lcd_byte(0x80, 0)
    msg1 = linha1.ljust(16)[:16]
    for char in msg1:
        lcd_byte(ord(char), LCD_RS)

    lcd_byte(0xC0, 0)
    msg2 = linha2.ljust(16)[:16]
    for char in msg2:
        lcd_byte(ord(char), LCD_RS)

def ler_distancia():
    """Mede a distância com o sensor ultrassônico"""
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

def acionar_buzzer(duracao_segundos):
    global buzzer_ligado, tempo_inicio_buzzer, duracao_buzzer
    pi.write(BUZZER_PIN, 1)
    buzzer_ligado = True
    tempo_inicio_buzzer = time.time()
    duracao_buzzer = duracao_segundos

def atualizar_buzzer():
    global buzzer_ligado
    if buzzer_ligado and (time.time() - tempo_inicio_buzzer) >= duracao_buzzer:
        pi.write(BUZZER_PIN, 0)
        buzzer_ligado = False

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

def processar_senha(senha_digitada):
    global falhas_consecutivas, sistema_destravado
    hash_digitado = hashlib.sha256(senha_digitada.encode()).hexdigest()
    
    if hash_digitado == SENHA_CORRETA_HASH:
        acionar_buzzer(0.2) 
        atualizar_lcd("Aberto", "Acesso Permitido")
        falhas_consecutivas = 0
        sistema_destravado = True 
        print("[SISTEMA] Tranca destravada.")
    else:
        acionar_buzzer(1.0) 
        falhas_consecutivas += 1
        atualizar_lcd("Acesso Negado", f"Falhas: {falhas_consecutivas}")
        print(f"[SISTEMA] Falha de autenticacao. Tentativa nº {falhas_consecutivas}")

def main():
    global buffer_senha, sistema_destravado
    
    lcd_init()
    atualizar_lcd("STATUS: OK", "Aguardando...")
    
    distancia_anterior = 0.0 
    
    try:
        while True:
            atualizar_buzzer()
            
            distancia = ler_distancia()

            print(distancia)
            
            if distancia > 0:
                if abs(distancia - distancia_anterior) >= 1.0:
                    print(f"[SENSOR] Distancia medida: {distancia} cm")
                    distancia_anterior = distancia
                
                if distancia > LIMITE_PORTA_FECHADA_CM and not sistema_destravado:
                    atualizar_lcd("ALARME!", "Invasao detectada")
                    acionar_buzzer(2.0)
                
                elif distancia <= LIMITE_PORTA_FECHADA_CM and sistema_destravado:
                    sistema_destravado = False
                    atualizar_lcd("STATUS: OK", "Porta Trancada")
                    print("[SISTEMA] Porta foi fechada. Sistema rearmado.")
            
            tecla = ler_teclado()
            
            if tecla:
                if tecla == '#': 
                    if len(buffer_senha) > 0:
                        processar_senha(buffer_senha)
                        buffer_senha = "" 
                        time.sleep(1.5) 
                        if not sistema_destravado:
                            atualizar_lcd("STATUS: OK", "Aguardando...")
                
                elif tecla == '*': 
                    buffer_senha = ""
                    atualizar_lcd("Entrada limpa", "Aguardando...")
                    
                else: 
                    buffer_senha += tecla
                    atualizar_lcd("Senha:", "*" * len(buffer_senha))
            
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[SISTEMA] Encerrando fechadura eletrônica...")
    finally:
        pi.write(BUZZER_PIN, 0)
        pi.write(TRIG_PIN, 0)
        if lcd_handle is not None:
            lcd_byte(0x01, 0) 
            pi.i2c_write_byte(lcd_handle, 0x00) 
            pi.i2c_close(lcd_handle)
        pi.stop()

if __name__ == '__main__':
    main()
