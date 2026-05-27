#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "ESP32_Calculadora_Divas";
const char* password = "12345678password";

WebServer server(80);

#define LED_BIT_0 4
#define LED_BIT_1 5
#define LED_BIT_2 6
#define LED_BIT_3 7

const char HTML_INTERFACE[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta name='viewport' content='width=device-width, initial-scale=1' charset='utf-8'>
    <title>Calculadora 4-bits Complemento de 2</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 30px; background-color: #f4f4f9; color: #333; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; box-sizing: border-box; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #008CBA; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #007B9A; }
        .result-box { margin-top: 20px; padding: 15px; background: #e7f3fe; border-left: 6px solid #2196F3; font-size: 18px; font-weight: bold; }
        .overflow-box { background: #fde8e8; border-left: 6px solid #f05252; color: #a82020; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Calculadora 4-bits (Complemento de 2)</h2>
        <p>Insira valores entre -8 e 7</p>
        
        <label>Operando A:</label>
        <input type="number" id="opA" min="-8" max="7" value="0">
        
        <label>Operação:</label>
        <select id="operacao">
            <option value="soma">Soma (+)</option>
            <option value="subtracao">Subtração (-)</option>
        </select>
        
        <label>Operando B:</label>
        <input type="number" id="opB" min="-8" max="7" value="0">
        
        <button onclick="enviarDados()">Calcular no ESP32</button>
        
        <div class="result-box" id="resultado_display">Resultado: -</div>
    </div>

    <script>
        function enviarDados() {
            let a = parseInt(document.getElementById('opA').value);
            let b = parseInt(document.getElementById('opB').value);
            let op = document.getElementById('operacao').value;
            if (a < -8 || a > 7 || b < -8 || b > 7 || isNaN(a) || isNaN(b)) {
                alert("Por favor, insira números apenas entre -8 e 7!");
                return;
            }
            
            let display = document.getElementById('resultado_display');
            
            fetch(`/calcular?a=${a}&b=${b}&op=${op}`)
                .then(response => response.text())
                .then(resultado => {
                    if (resultado === "OVERFLOW") {
                        display.innerText = "⚠️ OVERFLOW!";
                        display.className = "result-box overflow-box"; // Aplica estilo visual vermelho
                    } else {
                        display.innerText = "Resultado ULA: " + resultado;
                        display.className = "result-box"; // Mantém o estilo visual azul padrão
                    }
                });
        }
    </script>
</body>
</html>
)rawliteral";

void atualizarLedsFisicos(int8_t valor) {
  uint8_t valor4bits = (uint8_t)valor & 0x0F; 

  digitalWrite(LED_BIT_0, (valor4bits >> 0) & 0x01);
  digitalWrite(LED_BIT_1, (valor4bits >> 1) & 0x01);
  digitalWrite(LED_BIT_2, (valor4bits >> 2) & 0x01);
  digitalWrite(LED_BIT_3, (valor4bits >> 3) & 0x01);
}

void handleRoot() {
  server.send(200, "text/html", HTML_INTERFACE);
}

void handleCalcular() {
  if (server.hasArg("a") && server.hasArg("b") && server.hasArg("op")) {
    int inputA = server.arg("a").toInt();
    int inputB = server.arg("b").toInt();
    String op = server.arg("op");
    
    int8_t operandoA = (int8_t)((inputA & 0x0F) << 4) >> 4;
    int8_t operandoB = (int8_t)((inputB & 0x0F) << 4) >> 4;
    
    int raw_resultado = 0;
    int8_t b_ajustado = operandoB;
    
    if (op == "soma") {
      raw_resultado = operandoA + operandoB;
    } 
    else if (op == "subtracao") {
      raw_resultado = operandoA - operandoB;
      b_ajustado = -operandoB;
    }
  
    int8_t resultado4bits = (int8_t)((raw_resultado & 0x0F) << 4) >> 4;
    
    atualizarLedsFisicos(resultado4bits);
    
    bool overflow = false;

    if (operandoA >= 0 && b_ajustado >= 0 && resultado4bits < 0) {
      overflow = true;
    }
    else if (operandoA < 0 && b_ajustado < 0 && resultado4bits >= 0) {
      overflow = true;
    }
    if (overflow) {
      server.send(200, "text/plain", "OVERFLOW");
    } else {
      server.send(200, "text/plain", String(resultado4bits));
    }
    
  } else {
    server.send(400, "text/plain", "Parâmetros inválidos.");
  }
}

void setup() {
  Serial.begin(115200);
  
  pinMode(LED_BIT_0, OUTPUT);
  pinMode(LED_BIT_1, OUTPUT);
  pinMode(LED_BIT_2, OUTPUT);
  pinMode(LED_BIT_3, OUTPUT);
  
  atualizarLedsFisicos(0);

  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();

  server.on("/", handleRoot);
  server.on("/calcular", handleCalcular);
  
  server.begin();
}

void loop() {
  server.handleClient();
  delay(2);
}