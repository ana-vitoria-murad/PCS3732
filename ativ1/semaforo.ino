void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  rgbLedWrite(LED_BUILTIN, 0, 255, 0);
  delay(3000); 
  rgbLedWrite(LED_BUILTIN, 255, 255, 0);
  delay(1000);
  rgbLedWrite(LED_BUILTIN, 255, 0, 0);
  delay(4000);
}