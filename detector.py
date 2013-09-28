import wiringpi2
from time import time, sleep
INPUT = 0
OUTPUT = 1
PWM_OUTPUT = 2
LOW = 0
HIGH = 1
PUD_OFF = 0
PUD_DOWN = 1
PUD_UP = 2

# Use wiringPi numbering scheme - pin1 is PWM (PCM_CLK)
wiringpi2.wiringPiSetup()

# PIR connector on pin 0
MOTION_PIN = 0
# LED array on pin 1
LED_PIN = 1

BRIGHTNESS_MIN = 30
BRIGHTNESS_MAX = 1024
# How long should the LED take to go from 0 to 1
FADE_DURATION = 5
# How long after motion is detected do we believe there's no motion?
NO_MOTION_DURATION = 5
# How many times per second should we read the GPIO?
FREQUENCY = 20


BRIGHTNESS_RANGE = BRIGHTNESS_MAX - BRIGHTNESS_MIN
STEP = BRIGHTNESS_RANGE/FREQUENCY/FADE_DURATION

wiringpi2.pinMode(MOTION_PIN, INPUT)
wiringpi2.pullUpDnControl(MOTION_PIN, PUD_DOWN)
wiringpi2.pinMode(LED_PIN, PWM_OUTPUT)

brightness = 0
motionDetected = 0

while True:
  if wiringpi2.digitalRead(MOTION_PIN):
    motionDetected = time()

  if time() - motionDetected < 5:
    brightness += STEP
  else:
    brightness -= STEP

  if brightness < BRIGHTNESS_MIN:
    brightness = BRIGHTNESS_MIN
  if brightness > BRIGHTNESS_MAX:
    brightness = BRIGHTNESS_MAX

  wiringpi2.pwmWrite(LED_PIN, brightness)

  sleep(1.0/FREQUENCY)
