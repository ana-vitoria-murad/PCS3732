#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projeto: Fechadura Eletrônica com Raspberry Pi 3
Componentes: Teclado Matricial 4x4, Display LCD 16x2 (I2C), Sensor Ultrassônico HC-SR04, Buzzer.
Arquitectura: Orientada a Objetos com Máquina de Estados Não-Bloqueante.
"""

import pigpio
import time
import sys

# =====================================================================
# 1. CONFIGURAÇÕES E MAPEAMENTO DE PINOS (GPIOs BCM)
# =====================================================================
PINO_BUZZER = 12
PINO_TRIG   = 14
PINO_ECHO   = 15

LINHAS_TECLADO  = [26, 21, 20, 16]
COLUNAS_TECLADO = [5, 6, 13, 19]

I2C_BUS       = 1
ENDERECO_LCD  = 0x27  # Mude para 0x3F se o seu módulo exigir
LIMITE_PORTA_CM = 10.0
SENHA_MESTRE  = "1234" # Senha de acesso

# =====================================================================
# 2. CLASSES DOS COMPONENTES ISOLADOS
# =====================================================================

class Buzzer:
    def __init__(self, pi, pino):
        self.pi = pi
        self.pino = pino
        self.ligado = False
        self.tempo_inicio = 0
        self.duracao = 0
        self.pi.set_mode(self.pino, pigpio.OUTPUT)
        self.pi.write(self.pino, 0)

    def acionar(self, duracao_segundos):
        """Aciona o buzzer de forma NÃO-BLOQUEANTE."""
        self.pi.write(self.pino, 1)
        self.ligado = True
        self.tempo_inicio = time.time()
        self.duracao = duracao_segundos

    def bipe_curto(self):
        self.acionar(0.08)

    def bipe_sucesso(self):
        self.acionar(0.4)

    def bipe_erro(self):
        # Para erro, fazemos um bipe contínuo mais longo
        self.acionar(0.8)

    def atualizar(self):
        """Deve ser chamado a cada iteração do loop principal."""
        if self.ligado and (time.time() - self.tempo_inicio) >= self.duracao:
            self.pi.write(self.pino, 0)
            self.ligado = False

    def limpar(self):
        self.pi.write(self.pino, 0)


class DisplayLCD:
    LCD_BACKLIGHT = 0x08
    LCD_ENABLE    = 0x04
    LCD_RS        = 0x01

    def __init__(self, pi, bus, endereco):
        self.pi = pi
        self.handle = self.pi.i2c_open(bus, endereco)
        self._inicializar()

    def _toggle_enable(self, bits):
        self.pi.i2c_write_byte(self.handle, (bits | self.LCD_ENABLE))
        time.sleep(0.0005)
        self.pi.i2c_write_byte(self.handle, (bits & ~self.LCD_ENABLE))
        time.sleep(0.0001)

    def _enviar_byte(self, bits, modo):
        bits_high = modo | (bits & 0xF0) | self.LCD_BACKLIGHT
        bits_low  = modo | ((bits << 4) & 0xF0) | self.LCD_BACKLIGHT
        self.pi.i2c_write_byte(self.handle, bits_high)
        self._toggle_enable(bits_high)
        self.pi.i2c_write_byte(self.handle, bits_low)
        self._toggle_enable(bits_low)

    def _inicializar(self):
        time.sleep(0.05)
        for cmd in [0x33, 0x32, 0x06, 0x0C, 0x28, 0x01]:
            self._enviar_byte(cmd, 0)
        time.sleep(0.005)

    def exibir(self, linha1, linha2=""):
        """Atualiza as duas linhas do display instantaneamente."""
        # Linha 1
        self._enviar_byte(0x80, 0)
        for char in linha1.ljust(16)[:16]:
            self._enviar_byte(ord(char), self.LCD_RS)
        # Linha 2
        self._enviar_byte(0xC0, 0)
        for char in linha2.ljust(16)[:16]:
            self._enviar_byte(ord(char), self.LCD_RS)

    def limpar(self):
        self._enviar_byte(0x01, 0)
        time.sleep(0.002)

    def fechar(self):
        try:
            self.limpar()
            self.pi.i2c_write_byte(self.handle, 0x00)
            self.pi.i2c_close(self.handle)
        except Exception:
            pass


class SensorUltrassonico:
    def __init__(self, pi, pino_trig, pino_echo, limite_cm):
        self.pi = pi
        self.trig = pino_trig
        self.echo = pino_echo
        self.limite_cm = limite_cm
        self.pi.set_mode(self.trig, pigpio.OUTPUT)
        self.pi.set_mode(self.echo, pigpio.INPUT)
        self.pi.write(self.trig, 0)

    def ler_distancia(self):
        """Realiza leitura com timeout de segurança para não travar o loop."""
        self.pi.write(self.trig, 1)
        time.sleep(0.00001)
        self.pi.write(self.trig, 0)

        inicio_pulso = time.perf_counter()
        fim_pulso = time.perf_counter()
        timeout = time.perf_counter()

        while self.pi.read(self.echo) == 0:
            inicio_pulso = time.perf_counter()
            if inicio_pulso - timeout > 0.015:  # Timeout de 15ms
                return -1.0

        while self.pi.read(self.echo) == 1:
            fim_pulso = time.perf_counter()
            if fim_pulso - inicio_pulso > 0.015:
                return -1.0

        distancia = ((fim_pulso - inicio_pulso) * 34300) / 2
        return round(distancia, 2)

    def porta_fechada(self):
        dist = self.ler_distancia()
        if dist < 0:
            return None  # Erro de leitura/timeout
        return dist <= self.limite_cm


class TecladoMatricial:
    MATRIZ = [
        ['1', '4', '7', '*'],
        ['2', '5', '8', '0'],
        ['3', '6', '9', '#'],
        ['A', 'B', 'C', 'D']
    ]

    def __init__(self, pi, linhas, colunas):
        self.pi = pi
        self.linhas = linhas
        self.colunas = colunas
        self.tecla_anterior = None

        for col in self.colunas:
            self.pi.set_mode(col, pigpio.OUTPUT)
            self.pi.write(col, 1)

        for lin in self.linhas:
            self.pi.set_mode(lin, pigpio.INPUT)
            self.pi.set_pull_up_down(lin, pigpio.PUD_UP)
            self.pi.set_glitch_filter(lin, 50000) # Filtro de rebote via hardware

    def ler_tecla(self):
        tecla_atual = None
        for j in range(4):
            self.pi.write(self.colunas[j], 0)
            for i in range(4):
                if self.pi.read(self.linhas[i]) == 0:
                    tecla_atual = self.MATRIZ[i][j]
            self.pi.write(self.colunas[j], 1)
            if tecla_atual:
                break

        if tecla_atual != self.tecla_anterior:
            self.tecla_anterior = tecla_atual
            return tecla_atual
        return None

    def limpar(self):
        for col in self.colunas:
            self.pi.write(col, 1)


# =====================================================================
# 3. CONTROLADOR PRINCIPAL (MÁQUINA DE ESTADOS)
# =====================================================================

class FechaduraEletronica:
    def __init__(self, pi):
        self.pi = pi
        self.buzzer = Buzzer(pi, PINO_BUZZER)
        self.lcd = DisplayLCD(pi, I2C_BUS, ENDERECO_LCD)
        self.sensor = SensorUltrassonico(pi, PINO_TRIG, PINO_ECHO, LIMITE_PORTA_CM)
        self.teclado = TecladoMatricial(pi, LINHAS_TECLADO, COLUNAS_TECLADO)

        # Estados: 'TRAVADO', 'DESTRAVADO', 'ERRO'
        self.estado = 'TRAVADO'
        self.buffer_senha = ""
        
        # Variáveis de temporização não-bloqueante
        self.tempo_mudanca_estado = time.time()
        self.tempo_ultima_leitura_sensor = 0
        self.status_porta = "FECHADA"

        self.atualizar_interface()

    def mudar_estado(self, novo_estado):
        print(f"[MEF] Mudança de Estado: {self.estado} -> {novo_estado}")
        self.estado = novo_estado
        self.tempo_mudanca_estado = time.time()
        self.buffer_senha = ""
        self.atualizar_interface()

    def atualizar_interface(self):
        """Atualiza o LCD de acordo com o estado atual."""
        if self.estado == 'TRAVADO':
            mascara_senha = "*" * len(self.buffer_senha)
            self.lcd.exibir(f"PORTA: {self.status_porta}", f"Senha: {mascara_senha}")
        elif self.estado == 'DESTRAVADO':
            self.lcd.exibir("ACESSO PERMITIDO", f"Porta: {self.status_porta}")
        elif self.estado == 'ERRO':
            self.lcd.exibir("SENHA INCORRETA!", "Tente novamente.")

    def gerenciar_teclado(self):
        tecla = self.teclado.ler_tecla()
        if not tecla:
            return

        self.buzzer.bipe_curto()
        print(f"[TECLADO] Tecla: {tecla}")

        if self.estado == 'TRAVADO':
            if tecla == '*':
                # ' * ' limpa o buffer digitado
                self.buffer_senha = ""
                self.atualizar_interface()
            elif tecla == '#':
                # ' # ' avalia a senha digitada
                if self.buffer_senha == SENHA_MESTRE:
                    self.buzzer.bipe_sucesso()
                    self.mudar_estado('DESTRAVADO')
                else:
                    self.buzzer.bipe_erro()
                    self.mudar_estado('ERRO')
            else:
                # Acumula até 4 dígitos
                if len(self.buffer_senha) < 4:
                    self.buffer_senha += str(tecla)
                    self.atualizar_interface()
        
        elif self.estado == 'DESTRAVADO':
            # Se apertar '#' com a porta aberta/destravada, tranca manualmente
            if tecla == '#':
                self.mudar_estado('TRAVADO')

    def gerenciar_sensor(self):
        """Lê o sensor ultrassônico apenas a cada 500ms para poupar CPU."""
        if (time.time() - self.tempo_ultima_leitura_sensor) >= 0.5:
            self.tempo_ultima_leitura_sensor = time.time()
            fechada = self.sensor.porta_fechada()
            
            if fechada is not None:
                novo_status = "FECHADA" if fechada else "ABERTA"
                if novo_status != self.status_porta:
                    print(f"[SENSOR] Status da Porta mudou para: {novo_status}")
                    self.status_porta = novo_status
                    # Atualiza o display se estiver no modo normal
                    if self.estado in ['TRAVADO', 'DESTRAVADO']:
                        self.atualizar_interface()

    def gerenciar_temporizadores(self):
        """Controla o retorno automático de estados temporários."""
        tempo_decorrido = time.time() - self.tempo_mudanca_estado

        # Sai do estado de ERRO após 2 segundos
        if self.estado == 'ERRO' and tempo_decorrido >= 2.0:
            self.mudar_estado('TRAVADO')

        # Trava automaticamente após 6 segundos destravada (se a porta estiver fechada)
        elif self.estado == 'DESTRAVADO' and tempo_decorrido >= 6.0:
            if self.status_porta == "FECHADA":
                print("[SISTEMA] Trancamento automático por tempo.")
                self.buzzer.bipe_curto()
                self.mudar_estado('TRAVADO')

    def rodar(self):
        print("[SISTEMA] Fechadura Eletrônica Iniciada. Aguardando comandos...")
        try:
            while True:
                # O laço roda em altíssima frequência, sem nenhum sleep() bloqueante
                self.buzzer.atualizar()
                self.gerenciar_teclado()
                self.gerenciar_sensor()
                self.gerenciar_temporizadores()
                time.sleep(0.01) # Pequena pausa de 10ms apenas para não esgotar 100% da CPU
                
        except KeyboardInterrupt:
            print("\n[SISTEMA] Desligando fechadura...")
        finally:
            self.buzzer.limpar()
            self.lcd.fechar()
            self.teclado.limpar()
            self.pi.stop()
            print("[SISTEMA] Conexões GPIO e I2C encerradas com segurança.")

# =====================================================================
# 4. EXECUÇÃO PRINCIPAL
# =====================================================================
if __name__ == '__main__':
    pi = pigpio.pi()
    if not pi.connected:
        print("[ERRO FATAL] Falha ao conectar ao daemon pigpio.")
        print("Execute no terminal: sudo pigpiod")
        sys.exit(1)

    try:
        fechadura = FechaduraEletronica(pi)
        fechadura.rodar()
    except Exception as e:
        print(f"[ERRO INESPERADO] {e}")
        pi.stop()
