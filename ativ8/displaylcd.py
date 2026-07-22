import pigpio
import time
import sys

I2C_BUS = 1
ENDERECO_LCD = 0x27 

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

def enviar_comando_lcd(comando):
    try:
        pi.i2c_write_byte_data(lcd_handle, 0x80, comando)
    except Exception as e:
        print(f"Erro no barramento I2C via pigpio: {e}")

def exibir_mensagem(msg):
    print(f"LCD EXIBE: {msg}")

if __name__ == '__main__':
    try:
        exibir_mensagem("STATUS: OK")
        time.sleep(2)
        exibir_mensagem("Senha: ****")
    finally:
        pi.i2c_close(lcd_handle)
        pi.stop()
