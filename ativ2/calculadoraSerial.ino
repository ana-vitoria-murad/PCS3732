#include <Arduino.h>

#define LED_BIT_0 4
#define LED_BIT_1 5
#define LED_BIT_2 6
#define LED_BIT_3 7

void atualizarLedsFisicos(uint8_t valor4bits) {
  digitalWrite(LED_BIT_0, (valor4bits >> 0) & 0x01);
  digitalWrite(LED_BIT_1, (valor4bits >> 1) & 0x01);
  digitalWrite(LED_BIT_2, (valor4bits >> 2) & 0x01);
  digitalWrite(LED_BIT_3, (valor4bits >> 3) & 0x01);
}

void printBinario4Bits(uint8_t valor) {
  for (int i = 3; i >= 0; i--) {
    Serial.print((valor >> i) & 0x01);
  }
}

uint8_t paraComplementoDeUm(int valor) {
  if (valor >= 0) {
    return (uint8_t)valor & 0x0F;
  } else {
    return (uint8_t)(~abs(valor)) & 0x0F;
  }
}

int paraInteiroSinalizado(uint8_t comp1) {
  comp1 &= 0x0F;
  if (comp1 & 0x08) {
    return -((~comp1) & 0x0F);
  }
  return comp1;
}

void executarULA(int valA, int valB, char op) {
  uint8_t a = paraComplementoDeUm(valA);
  uint8_t b = paraComplementoDeUm(valB);

  if (op == '-') {
    b = (~b) & 0x0F; 
  }

  uint16_t soma_raw = (uint16_t)a + (uint16_t)b;
  uint8_t resultado = soma_raw & 0x0F;

  if (soma_raw & 0x10) {
    resultado = (resultado + 1) & 0x0F;
    Serial.println("[ULA Info] End-Around Carry detectado! Somando +1 ao LSB.");
  }
  
  atualizarLedsFisicos(resultado);
  
  Serial.println("\n--- RELATÓRIO DA OPERAÇÃO DE 4 BITS (COMPLEMENTO DE 1) ---");
  Serial.print("Operando A decimal: "); Serial.print(valA); Serial.print("  | Binário: "); printBinario4Bits(a); Serial.println();
  Serial.print("Operando B decimal: "); Serial.print(op == '-' ? -valB : valB); Serial.print("  | Binário: "); printBinario4Bits(b); Serial.println();
  Serial.println("-------------------------------------------------------");
  Serial.print("Resultado Binário: "); printBinario4Bits(resultado); Serial.println();
  
  int resDecimal = paraInteiroSinalizado(resultado);
  Serial.print("Resultado Decimal Interpretado: "); 

  if (resultado == 0x0F) {
    Serial.println("-0 (Zero Negativo)");
  } else {
    Serial.println(resDecimal);
  }
  Serial.println("=======================================================\n");
}

void setup() {
  Serial.begin(115200);
  
  pinMode(LED_BIT_0, OUTPUT);
  pinMode(LED_BIT_1, OUTPUT);
  pinMode(LED_BIT_2, OUTPUT);
  pinMode(LED_BIT_3, OUTPUT);
  
  atualizarLedsFisicos(0);
  
  delay(2000);
  Serial.println("Digite o comando no formato: A [operacao] B (Exemplo: 5 + 2 ou 3 - 4)");
  Serial.println("Valores permitidos: -7 até 7");
  Serial.println("-------------------------------------------------------");
}

void loop() {
  if (Serial.available() > 0) {
    int inputA = Serial.parseInt();
    char operacao = Serial.read();

    while (operacao == ' ') {
      operacao = Serial.read();
    }
    
    int inputB = Serial.parseInt();

    while (Serial.available() > 0) { Serial.read(); }

    if (inputA < -7 || inputA > 7 || inputB < -7 || inputB > 7) {
      Serial.println("[ERRO] Os valores devem estar estritamente entre -7 e 7.");
      return;
    }

    if (operacao == '+' || operacao == '-') {
      executarULA(inputA, inputB, operacao);
    } else {
      Serial.println("[ERRO] Operação inválida. Utilize + ou -.");
    }
  }
}