#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "sensorLDR_Divas";
const char* password = "1234567password";

#define LDR_PIN 4

WebServer server(80);

unsigned long previousMillis = 0;
const long interval = 2000;
bool ledState = LOW;

const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>ESP32 LDR Web Server</title>
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
  <h1>Monitor de Luminosidade</h1>
  <div class="sensor-box">
    <p>Valor ADC (Quanto maior, mais escuro):</p>
    <p class="value" id="ldr_value">Carregando...</p>
  </div>
</body>
</html>
)rawliteral";

void handleRoot() { server.send(200, "text/html", htmlPage); }
void handleLDR() { server.send(200, "text/plain", String(analogRead(LDR_PIN))); }

void setup() {
  Serial.begin(115200);

  pinMode(LED_BUILTIN, OUTPUT);

  WiFi.softAP(ssid, password);
  server.on("/", handleRoot);
  server.on("/ldr", handleLDR);
  server.begin();
  
  Serial.println("Servidor iniciado.");
}

void loop() {
  server.handleClient();

  int ldrValue = analogRead(LDR_PIN);
  unsigned long currentMillis = millis();

  if (ldrValue > 2000) {
    if (currentMillis - previousMillis >= interval) {
      previousMillis = currentMillis;
      ledState = !ledState;
      
      if (ledState) {
        rgbLedWrite(LED_BUILTIN, 255, 255, 0);
      } else {
        rgbLedWrite(LED_BUILTIN, 0, 0, 0);
      }
    }
  } else {
    rgbLedWrite(LED_BUILTIN, 0, 0, 0);
    ledState = LOW;
  }
}