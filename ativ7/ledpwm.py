from gpiozero import PWMLED
from time import sleep

LED_PIN = 18
led = PWMLED(LED_PIN)

print("1 Hz")
led.frequency = 1
led.value = 0.5
sleep(4)

print("10 Hz")
led.frequency = 10
led.value = 0.5
sleep(4)

print("100 Hz")
led.frequency = 100
led.value = 0.25
sleep(3)
led.value = 1.0
sleep(3)

led.off()
