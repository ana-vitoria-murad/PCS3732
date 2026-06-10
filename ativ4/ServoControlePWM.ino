#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

const char* ssid = "ESP32_Controle_Servo_Divas";
const char* password = "12345678password";

WebServer server(80);

Servo meuServo;
#define SERVO_PIN 4
int anguloAtual = 90;

const char HTML_INTERFACE[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta name='viewport' content='width=device-width, initial-scale=1' charset='utf-8'>
    <title>Controle de Servomotor</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 30px; background-color: #f4f4f9; color: #333; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input, button { width: 100%; padding: 12px; margin: 8px 0; box-sizing: border-box; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #ff5722; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #e64a19; }
        .slider-container { margin: 15px 0; text-align: left; }
        .result-box { margin-top: 20px; padding: 15px; background: #ffebee; border-left: 6px solid #ff5722; font-size: 16px; font-weight: bold; }
        span { font-weight: bold; color: #d84315; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Controle do Servo</h2>
        <p>Ajuste a posição do eixo do motor</p>
        
        <div class="slider-container">
            <label>Ângulo: <span id="valAngulo">90</span>&deg;</label>
            <input type="range" id="angulo" min="0" max="180" value="90" oninput="atualizarLabel()">
        </div>
        
        <button onclick="enviarDados()">Atualizar Posição</button>
        
        <div class="result-box" id="status_display">Status: Pronto</div>
    </div>

    <script>
        function atualizarLabel() {
            document.getElementById('valAngulo').innerText = document.getElementById('angulo').value;
        }

        function enviarDados() {
            let angle = parseInt(document.getElementById('angulo').value);
            let display = document.getElementById('status_display');
            
            fetch(`/configurar?angulo=${angle}`)
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
  if (server.hasArg("angulo")) {
    int anguloReq = server.arg("angulo").toInt();

    if (anguloReq < 0) anguloReq = 0;
    if (anguloReq > 180) anguloReq = 180;

    anguloAtual = anguloReq;
    meuServo.write(anguloAtual);

    String resposta = String(anguloAtual) + " graus";
    server.send(200, "text/plain", resposta);
    
    Serial.println("Posição atualizada: " + resposta);
  } else {
    server.send(400, "text/plain", "Parâmetro inválido.");
  }
}

void setup() {
  Serial.begin(115200);

  ESP32PWM::allocateTimer(0);
  meuServo.setPeriodHertz(50);
  meuServo.attach(SERVO_PIN, 500, 2400); 
  meuServo.write(anguloAtual);

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