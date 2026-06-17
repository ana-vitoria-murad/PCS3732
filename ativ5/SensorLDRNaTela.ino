#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "sensorLDR_Divas";
const char* password = "1234567password";

#define LDR_PIN 4

WebServer server(80);

const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ESP32 LDR Web Server</title>
  <style>
    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }
    h1 { color: #333; }
    .sensor-box { display: inline-block; padding: 20px 40px; border-radius: 10px; background-color: #fff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .value { font-size: 3rem; font-weight: bold; color: #007BFF; }
  </style>
  <script>
    function fetchLDR() {
      fetch('/ldr')
        .then(response => response.text())
        .then(data => {
          document.getElementById("ldr_value").innerText = data;
        })
        .catch(error => console.error('Erro ao buscar dado do LDR:', error));
    }
    
    setInterval(fetchLDR, 1000);
  </script>
</head>
<body onload="fetchLDR()">
  <h1>Monitor de Luminosidade</h1>
  <div class="sensor-box">
    <p>Valor bruto do ADC (0 - 4095):</p>
    <p class="value" id="ldr_value">Carregando...</p>
  </div>
</body>
</html>
)rawliteral";

void handleRoot() {
  server.send(200, "text/html", htmlPage);
}

void handleLDR() {
  int ldrValue = analogRead(LDR_PIN);
  server.send(200, "text/plain", String(ldrValue));
}

void setup() {
  Serial.begin(115200);

  WiFi.softAP(ssid, password);
  server.on("/", handleRoot);
  server.on("/ldr", handleLDR);
  Serial.println("\nWiFi Conectado!");
  Serial.print("Endereço IP para acessar a interface web: ");
  IPAddress IP = WiFi.softAPIP();
  Serial.println(IP);

  server.begin();
  Serial.println("Servidor HTTP iniciado.");
}

void loop() {
  server.handleClient();
}