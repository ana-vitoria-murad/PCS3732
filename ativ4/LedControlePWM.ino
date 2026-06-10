#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "ESP32_Controle_PWM_Divas";
const char* password = "12345678password";

WebServer server(80);

#define LED_PIN 4

const int resolution = 13;

int frequenciaAtual = 1000;
int intensidadeAtual = 50;

const char HTML_INTERFACE[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta name='viewport' content='width=device-width, initial-scale=1' charset='utf-8'>
    <title>Controle de LED via PWM</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 30px; background-color: #f4f4f9; color: #333; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input, button { width: 100%; padding: 12px; margin: 8px 0; box-sizing: border-box; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #4CAF50; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #45a049; }
        .slider-container { margin: 15px 0; text-align: left; }
        .result-box { margin-top: 20px; padding: 15px; background: #e7f3fe; border-left: 6px solid #2196F3; font-size: 16px; font-weight: bold; }
        span { font-weight: bold; color: #008CBA; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Controle de LED (PWM)</h2>
        <p>Ajuste a frequência e o brilho do LED externo</p>
        
        <div class="slider-container">
            <label>Intensidade (Brilho): <span id="valBrilho">50</span>%</label>
            <input type="range" id="intensidade" min="0" max="100" value="50" oninput="atualizarLabel()">
        </div>
        
        <div class="slider-container">
            <label>Frequência (Hz):</label>
            <input type="number" id="frequencia" min="1" max="40000" value="1000">
        </div>
        
        <button onclick="enviarDados()">Atualizar Parâmetros</button>
        
        <div class="result-box" id="status_display">Status: Pronto</div>
    </div>

    <script>
        function atualizarLabel() {
            document.getElementById('valBrilho').innerText = document.getElementById('intensidade').value;
        }

        function enviarDados() {
            let freq = parseInt(document.getElementById('frequencia').value);
            let intensity = parseInt(document.getElementById('intensidade').value);
            
            if (freq < 1 || freq > 40000 || isNaN(freq)) {
                alert("Por favor, insira uma frequência válida entre 1 e 40000 Hz!");
                return;
            }
            
            let display = document.getElementById('status_display');
            
            fetch(`/configurar?freq=${freq}&intensidade=${intensity}`)
                .then(response => response.text())
                .then(resultado => {
                    display.innerText = "Configurado: " + resultado;
                })
                .catch(err => {
                    display.innerText = "Erro ao comunicar com o ESP32";
                });
        }
    </script>
</body>
</html>
)rawliteral";

void handleRoot() {
  server.send(200, "text/html", HTML_INTERFACE);
}

void handleConfigurar() {
  if (server.hasArg("freq") && server.hasArg("intensidade")) {
    int freq = server.arg("freq").toInt();
    int intensidade = server.arg("intensidade").toInt();
    
    if (freq < 1) freq = 1;
    if (freq > 40000) freq = 40000; 
    if (intensidade < 0) intensidade = 0;
    if (intensidade > 100) intensidade = 100;

    frequenciaAtual = freq;
    intensidadeAtual = intensidade;

    int dutyCycle = (intensidade * 255) / 100;

    ledcChangeFrequency(LED_PIN, frequenciaAtual, resolution);
    ledcWrite(LED_PIN, dutyCycle);

    String resposta = String(frequenciaAtual) + " Hz @ " + String(intensidadeAtual) + "%";
    server.send(200, "text/plain", resposta);
    
    Serial.println("Configuração atualizada: " + resposta);
  } else {
    server.send(400, "text/plain", "Parâmetros inválidos.");
  }
}

void setup() {
  Serial.begin(115200);

  ledcAttach(LED_PIN, frequenciaAtual, resolution);
  int dutyInicial = (intensidadeAtual * 255) / 100;
  ledcWrite(LED_PIN, dutyInicial);

  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP Address: ");
  Serial.println(IP);

  server.on("/", handleRoot);
  server.on("/configurar", handleConfigurar);
  
  server.begin();
  Serial.println("Servidor Web pronto!");
}

void loop() {
  server.handleClient();
  delay(2);
}