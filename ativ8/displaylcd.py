import pigpio
import time
import sys

I2C_BUS = 1
ENDERECO_LCD = 0x27  # 0x3F 

LCD_BACKLIGHT = 0x08  
LCD_ENABLE    = 0x04  
LCD_RS        = 0x01  

pi = pigpio.pi()
if not pi.connected:
    print("[ERRO] Falha ao conectar ao daemon pigpio. Execute 'sudo pigpiod'.")
    sys.exit()

try:
    lcd_handle = pi.i2c_open(I2C_BUS, ENDERECO_LCD)
except Exception as e:
    print(f"[ERRO] Falha ao abrir conexão I2C: {e}")
    pi.stop()
    sys.exit()


def lcd_toggle_enable(bits):
    """Gera um pulso no pino Enable para o LCD processar o dado"""
    pi.i2c_write_byte(lcd_handle, (bits | LCD_ENABLE))
    time.sleep(0.0005)
    pi.i2c_write_byte(lcd_handle, (bits & ~LCD_ENABLE))
    time.sleep(0.0001)

def lcd_byte(bits, modo):
    """Envia 1 byte dividido em dois nibbles de 4 bits para o LCD"""
    bits_high = modo | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low  = modo | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # Envia os 4 bits mais significativos
    pi.i2c_write_byte(lcd_handle, bits_high)
    lcd_toggle_enable(bits_high)

    # Envia os 4 bits menos significativos
    pi.i2c_write_byte(lcd_handle, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_init():
    """Inicializa a tela no modo de 4 bits"""
    time.sleep(0.05)
    lcd_byte(0x33, 0) 
    lcd_byte(0x32, 0) 
    lcd_byte(0x06, 0) 
    lcd_byte(0x0C, 0) 
    lcd_byte(0x28, 0) 
    lcd_byte(0x01, 0) 
    time.sleep(0.005)

def exibir_mensagem(msg, linha=1):
    """Escreve a mensagem no terminal e na tela física do LCD (linha 1 ou 2)"""
    print(f"LCD EXIBE (Linha {linha}): {msg}")
    
    posicao_linha = 0x80 if linha == 1 else 0xC0
    lcd_byte(posicao_linha, 0)
    
    msg_formatada = msg.ljust(16)[:16]
    
    for char in msg_formatada:
        lcd_byte(ord(char), LCD_RS)

if __name__ == '__main__':
    try:
        lcd_init()

        exibir_mensagem("STATUS: OK", linha=1)
        exibir_mensagem("Senha: ****", linha=2)
        
        time.sleep(3)

        lcd_byte(0x01, 0) 
        time.sleep(0.002)
        exibir_mensagem("Acesso Permitido", linha=1)

    except KeyboardInterrupt:
        print("\n[SISTEMA] Encerramento solicitado pelo usuário.")
    finally:
        try:
            lcd_byte(0x01, 0) 
            pi.i2c_write_byte(lcd_handle, 0x00) 
            pi.i2c_close(lcd_handle)
        except Exception:
            pass
        pi.stop()
