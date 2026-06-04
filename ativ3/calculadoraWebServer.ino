#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "ESP32_Calculadora_Lab04";
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
    <title>Calculadora ESP32 Expansão</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 30px; background-color: #f4f4f9; color: #333; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; box-sizing: border-box; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #008CBA; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #007B9A; }
        .result-box { margin-top: 20px; padding: 15px; background: #e7f3fe; border-left: 6px solid #2196F3; font-size: 18px; font-weight: bold; }
        .error-box { background: #fde8e8; border-left: 6px solid #f05252; color: #a82020; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Calculadora ESP32 (Lab 04)</h2>
        <p>Valores aceitos: Inteiros (Sem limite)</p>
        
        <label>Operando A:</label>
        <input type="number" id="opA" value="0">
        
        <label>Operação:</label>
        <select id="operacao">
            <option value="soma">Soma (+)</option>
            <option value="subtracao">Subtração (-)</option>
            <option value="multiplicacao">Multiplicação (*)</option>
            <option value="divisao">Divisão (/)</option>
            <option value="fatorial">Fatorial (A!)</option>
        </select>
        
        <label>Operando B:</label>
        <input type="number" id="opB" value="0">
        
        <button onclick="enviarDados()">Calcular no ESP32</button>
        
        <div class="result-box" id="resultado_display">Resultado: -</div>
    </div>

    <script>
        function enviarDados() {
            let a = parseInt(document.getElementById('opA').value);
            let b = parseInt(document.getElementById('opB').value);
            let op = document.getElementById('operacao').value;
            
            if (op !== 'fatorial' && (isNaN(a) || isNaN(b))) {
                alert("Por favor, insira números válidos!");
                return;
            } else if (op === 'fatorial' && (a < 0 || isNaN(a))) {
                alert("Para fatorial, insira um número inteiro positivo (A >= 0)!");
                return;
            }
            
            let display = document.getElementById('resultado_display');
            fetch(`/calcular?a=${a}&b=${b}&op=${op}`)
                .then(response => response.text())
                .then(resultado => {
                    if (resultado === "DIV_ZERO") {
                        display.innerText = "⚠️ ERRO: Divisão por Zero!";
                        display.className = "result-box error-box";
                    } else {
                        display.innerText = "Resultado ULA: " + resultado;
                        display.className = "result-box"; 
                    }
                });
        }
    </script>
</body>
</html>
)rawliteral";

int multiply(int a, int b) {
    int result = 0;
    int abs_b = abs(b); 
    for (int i = 0; i < abs_b; i++) {
        result += a;
    }
    return (b < 0) ? -result : result;
}

int factorial(int n) {
    if (n <= 1) return 1;
    int result = 1;
    for(int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

int divide_op(int a, int b) {
    if (b == 0) return -1;
    return a / b;
}

void atualizarLedsFisicos(int valor) {
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
        int operandoA = server.arg("a").toInt();
        int operandoB = server.arg("b").toInt();
        String op = server.arg("op");
        
        int raw_resultado = 0;
        bool divisao_por_zero = false;
        
        uint32_t start_cycles = ESP.getCycleCount();
        
        if (op == "soma") {
            raw_resultado = operandoA + operandoB;
        } 
        else if (op == "subtracao") {
            raw_resultado = operandoA - operandoB;
        }
        else if (op == "multiplicacao") {
            raw_resultado = multiply(operandoA, operandoB);
        }
        else if (op == "fatorial") {
            raw_resultado = factorial(operandoA);
        }
        else if (op == "divisao") {
            if (operandoB == 0) {
                divisao_por_zero = true;
            } else {
                raw_resultado = divide_op(operandoA, operandoB);
            }
        }
        
        uint32_t end_cycles = ESP.getCycleCount();
        
        uint32_t elapsed_cycles = end_cycles - start_cycles;
        uint32_t cpu_freq_mhz = ESP.getCpuFreqMHz(); 
        
        double tempo_ns = ((double)elapsed_cycles * 1000.0) / cpu_freq_mhz;
        
        Serial.print("Operação: ");
        Serial.print(op);
        Serial.print(" | Ciclos da CPU: ");
        Serial.print(elapsed_cycles);
        Serial.print(" | Tempo de processamento: ");
        Serial.print(tempo_ns, 2); 
        Serial.println(" ns");
        
        if (divisao_por_zero) {
            server.send(200, "text/plain", "DIV_ZERO");
            return;
        }

        atualizarLedsFisicos(raw_resultado);
        
        server.send(200, "text/plain", String(raw_resultado));
        
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
    server.on("/", handleRoot);
    server.on("/calcular", handleCalcular);
    
    server.begin();
    
    Serial.println("Servidor iniciado.");
    Serial.print("Frequência da CPU: ");
    Serial.print(ESP.getCpuFreqMHz());
    Serial.println(" MHz");
}

void loop() {
    server.handleClient();
    delay(2);
}
