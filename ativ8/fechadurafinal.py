import pigpio
import time
import sys

BUZZER_PIN = 12 
LED_FECHADURA_PIN = 17 
TRIG_PIN = 14 
ECHO_PIN = 15 
LINHAS = [26, 21, 20, 16] 
COLUNAS = [5, 6, 13, 19] 

I2C_BUS = 1
ENDERECO_LCD = 0x27
LCD_BACKLIGHT = 0x08
LCD_ENABLE = 0x04
LCD_RS = 0x01

MATRIZ = [
    ['1', '4', '7', '*'],
    ['2', '5', '8', '0'],
    ['3', '6', '9', '#'],
    ['A', 'B', 'C', 'D']
]

SENHA_CORRETA = "1234"
LIMITE_DISTANCIA_CM = 30.0

buzzer_ligado = False 
tempo_inicio_buzzer = 0 
duracao_buzzer = 0 

led_ligado = False
tempo_inicio_led = 0
duracao_led = 0

tecla_anterior = None 
lcd_handle = None
estado_bloqueado = False
tempo_reset_display = 0

pi = pigpio.pi()
if not pi.connected:
    print("[ERRO] Falha ao conectar ao daemon pigpio. Execute 'sudo pigpiod'.") 
    sys.exit()

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

def acionar_led(duracao_segundos):
    global led_ligado, tempo_inicio_led, duracao_led
    pi.write(LED_FECHADURA_PIN, 1) 
    led_ligado = True
    tempo_inicio_led = time.time()
    duracao_led = duracao_segundos

def atualizar_led():
    global led_ligado
    if led_ligado:
        if (time.time() - tempo_inicio_led) >= duracao_led:
            pi.write(LED_FECHADURA_PIN, 0) 
            led_ligado = False

def lcd_toggle_enable(bits):
    pi.i2c_write_byte(lcd_handle, (bits | LCD_ENABLE)) 
    time.sleep(0.0005) 
    pi.i2c_write_byte(lcd_handle, (bits & ~LCD_ENABLE)) 
    time.sleep(0.0001) 

def lcd_byte(bits, modo):
    bits_high = modo | (bits & 0xF0) | LCD_BACKLIGHT 
    bits_low  = modo | ((bits << 4) & 0xF0) | LCD_BACKLIGHT 
    pi.i2c_write_byte(lcd_handle, bits_high) 
    lcd_toggle_enable(bits_high) 
    pi.i2c_write_byte(lcd_handle, bits_low) 
    lcd_toggle_enable(bits_low) 

def lcd_init():
    time.sleep(0.05) 
    lcd_byte(0x33, 0) 
    lcd_byte(0x32, 0) 
    lcd_byte(0x06, 0) 
    lcd_byte(0x0C, 0) 
    lcd_byte(0x28, 0) 
    lcd_byte(0x01, 0) 
    time.sleep(0.005) 

def exibir_mensagem(msg, linha=1):
    posicao_linha = 0x80 if linha == 1 else 0xC0 
    lcd_byte(posicao_linha, 0) 
    msg_formatada = msg.ljust(16)[:16] 
    for char in msg_formatada: 
        lcd_byte(ord(char), LCD_RS) 

def ler_distancia():
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

def setup():
    global lcd_handle
    
    pi.set_mode(BUZZER_PIN, pigpio.OUTPUT) 
    pi.write(BUZZER_PIN, 0) 
    pi.set_mode(LED_FECHADURA_PIN, pigpio.OUTPUT)
    pi.write(LED_FECHADURA_PIN, 0)
    
    pi.set_mode(TRIG_PIN, pigpio.OUTPUT) 
    pi.set_mode(ECHO_PIN, pigpio.INPUT) 
    pi.write(TRIG_PIN, 0) 
    
    for col in COLUNAS: 
        pi.set_mode(col, pigpio.OUTPUT) 
        pi.write(col, 1)  
    for lin in LINHAS: 
        pi.set_mode(lin, pigpio.INPUT) 
        pi.set_pull_up_down(lin, pigpio.PUD_UP) 
        pi.set_glitch_filter(lin, 50000)  

    try:
        lcd_handle = pi.i2c_open(I2C_BUS, ENDERECO_LCD) 
        lcd_init() 
    except Exception as e:
        print(f"[ERRO] I2C: {e}") 
        sys.exit()

if __name__ == '__main__':
    setup()
    senha_digitada = ""
    exibir_mensagem("STATUS: OK", linha=1) 
    exibir_mensagem("Senha: ", linha=2) 
    
    try:
        while True:
            atualizar_buzzer() 
            atualizar_led()
            
            if tempo_reset_display > 0 and time.time() > tempo_reset_display:
                exibir_mensagem("STATUS: OK", linha=1) 
                exibir_mensagem("Senha: ", linha=2) 
                senha_digitada = ""
                tempo_reset_display = 0

            distancia = ler_distancia() 
            
            if distancia > 0 and distancia > LIMITE_DISTANCIA_CM:
                if not estado_bloqueado:
                    estado_bloqueado = True
                    acionar_buzzer(3)  
                    exibir_mensagem("SISTEMA", linha=1)
                    exibir_mensagem("BLOQUEADO", linha=2)
                time.sleep(0.1)
                continue
            
            elif estado_bloqueado:
                estado_bloqueado = False
                senha_digitada = ""
                exibir_mensagem("STATUS: OK", linha=1) 
                exibir_mensagem("Senha: ", linha=2) 
            
            tecla = ler_teclado() 
            if tecla and tempo_reset_display == 0:
                senha_digitada += tecla
                
                exibir_mensagem("Senha: " + "*" * len(senha_digitada), linha=2)
                
                if len(senha_digitada) == len(SENHA_CORRETA):
                    if senha_digitada == SENHA_CORRETA:
                        exibir_mensagem("Acesso Permitido", linha=1) 
                        acionar_buzzer(1) 
                        acionar_led(3)    
                    else:
                        exibir_mensagem("Acesso Negado", linha=1) #
                        acionar_buzzer(2) 
                    
                    tempo_reset_display = time.time() + 3.0

            time.sleep(0.05) 
            
    except KeyboardInterrupt:
        print("\n[SISTEMA] Interrompido pelo usuário.") 
    finally:
        pi.write(BUZZER_PIN, 0) 
        pi.write(LED_FECHADURA_PIN, 0)
        pi.write(TRIG_PIN, 0) 
        for col in COLUNAS: 
            pi.write(col, 1) 
        try:
            lcd_byte(0x01, 0) 
            pi.i2c_write_byte(lcd_handle, 0x00) 
            pi.i2c_close(lcd_handle) 
        except Exception:
            pass
        pi.stop() 
