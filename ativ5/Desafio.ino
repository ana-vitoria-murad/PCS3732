#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "sensorLDR_Divas";
const char* password = "1234567password";

#define LDR_PIN 4
#define BTN_SOS 5

WebServer server(80);

enum EstadosSemaforo { VERDE, AMARELO, VERMELHO };
EstadosSemaforo estadoAtual = VERDE;
EstadosSemaforo estadoSalvo = VERDE;

unsigned long previousMillisSemaforo = 0;
unsigned long previousMillisNoturno = 0;
unsigned long tempoPedestreStart = 0;

unsigned long duracaoEstado = 3000;
bool ledStateNoturno = LOW;

volatile bool pedestre_solicitado = false;
bool modoPedestreAtivo = false;
bool modoNoturnoAtivo = false;
unsigned long ultimo_tempo_botao = 0;

const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>ESP32 LDR & Semáforo Web Server</title>
  <style>
    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }
    .sensor-box { display: inline-block; padding: 20px 40px; border-radius: 10px; background-color: #fff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .value { font-size: 3rem; font-weight: bold; color: #007BFF; }
  </style>
  <script>
    function fetchLDR() {
      fetch('/ldr').then(r => r.text()).then(d => document.getElementById("ldr_value").innerText = d);
    }
    setInterval(fetchLDR, 1000);
  </script>
</head>
<body onload="fetchLDR()">
  <h1>Monitor do Sistema de Trânsito</h1>
  <div class="sensor-box">
    <p>Valor ADC do LDR:</p>
    <p class="value" id="ldr_value">Carregando...</p>
  </div>
</body>
</html>
)rawliteral";

void handleRoot() { server.send(200, "text/html", htmlPage); }
void handleLDR() { server.send(200, "text/plain", String(analogRead(LDR_PIN))); }

void IRAM_ATTR isr_pedestre() {
  if (millis() - ultimo_tempo_botao > 250) {
    pedestre_solicitado = true;
    ultimo_tempo_botao = millis();
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(BTN_SOS, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BTN_SOS), isr_pedestre, FALLING);

  WiFi.softAP(ssid, password);
  server.on("/", handleRoot);
  server.on("/ldr", handleLDR);
  server.begin();
  
  Serial.println("Servidor e Semáforo Iniciados.");
}

void loop() {
  server.handleClient();
  unsigned long currentMillis = millis();
  int ldrValue = analogRead(LDR_PIN);
  if (ldrValue > 2500) { 
    if (!modoNoturnoAtivo) {
      estadoSalvo = estadoAtual;
      modoNoturnoAtivo = true;
      Serial.println("Modo Noturno Ativado (LDR Escuro).");
    }
  } else {
    if (modoNoturnoAtivo) {
      estadoAtual = estadoSalvo;
      modoNoturnoAtivo = false;
      previousMillisSemaforo = currentMillis;
      Serial.println("Modo Diurno Restaurado.");
    }
  }
  if (pedestre_solicitado && !modoNoturnoAtivo) {
    pedestre_solicitado = false;
    modoPedestreAtivo = true;
    tempoPedestreStart = currentMillis;
    estadoSalvo = estadoAtual;
    Serial.println("Pedestre solicitou travessia! Forçando Vermelho por 3s.");
  }

  if (modoPedestreAtivo) {
    if (currentMillis - tempoPedestreStart < 3000) {
      rgbLedWrite(LED_BUILTIN, 255, 0, 0);
      return;
    } else {
      modoPedestreAtivo = false;
      estadoAtual = estadoSalvo;
      previousMillisSemaforo = currentMillis;
      Serial.println("Travessia concluída. Retornando ao fluxo padrão.");
    }
  }
  if (modoNoturnoAtivo) {
    if (currentMillis - previousMillisNoturno >= 1000) {
      previousMillisNoturno = currentMillis;
      ledStateNoturno = !ledStateNoturno;
      if (ledStateNoturno) {
        rgbLedWrite(LED_BUILTIN, 255, 255, 0);
      } else {
        rgbLedWrite(LED_BUILTIN, 0, 0, 0);
      }
    }
  } 
  else {
    if (currentMillis - previousMillisSemaforo >= duracaoEstado) {
      previousMillisSemaforo = currentMillis;

      switch (estadoAtual) {
        case VERDE:
          estadoAtual = AMARELO;
          duracaoEstado = 1000;
          break;

        case AMARELO:
          estadoAtual = VERMELHO;
          duracaoEstado = 4000;
          break;

        case VERMELHO:
          estadoAtual = VERDE;
          duracaoEstado = 3000;
          break;
      }
    }

    if (estadoAtual == VERDE)      rgbLedWrite(LED_BUILTIN, 0, 255, 0);
    if (estadoAtual == AMARELO)    rgbLedWrite(LED_BUILTIN, 255, 255, 0);
    if (estadoAtual == VERMELHO)   rgbLedWrite(LED_BUILTIN, 255, 0, 0);
  }
}