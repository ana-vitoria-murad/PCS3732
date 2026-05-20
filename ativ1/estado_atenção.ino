void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  rgbLedWrite(LED_BUILTIN, 255, 255, 0);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000); 
}