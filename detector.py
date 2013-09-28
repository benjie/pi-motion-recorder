#!/usr/bin/env python
import os
import signal
import subprocess
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

MAX_STATUSES = 50


BRIGHTNESS_RANGE = BRIGHTNESS_MAX - BRIGHTNESS_MIN
STEP = BRIGHTNESS_RANGE/FREQUENCY/FADE_DURATION

wiringpi2.pinMode(MOTION_PIN, INPUT)
wiringpi2.pullUpDnControl(MOTION_PIN, PUD_DOWN)
wiringpi2.pinMode(LED_PIN, PWM_OUTPUT)

brightness = 0
notifiedBrightness = 0
motionDetected = 0
notified = 0
recording = False
recording_process = None
formatted_date = None
statuses = []

def add_video(string):
  with open("/capture/videos.txt", "a") as myfile:
    myfile.write("%s\n" % (string))

def add_entry(string):
  global statuses
  status = "%f:%s" % (time(), string)
  statuses.append(status)
  if len(statuses) > MAX_STATUSES:
    statuses = statuses[-MAX_STATUSES:]
  with open("/capture/log.txt", "w") as myfile:
    myfile.write("\n".join(statuses))

def start_recording():
  global recording, recording_process, formatted_date
  if recording:
    return
  recording = True
  print "Starting recording..."
  #recording_process = subprocess.Popen(['bash', './record.sh'])
  formatted_date = subprocess.check_output("date +'%Y-%m-%d_%H-%M-%S'", shell = True).strip()
  add_entry("RECORDING:"+formatted_date)
  command = "raspivid -w 1280 -h 720 -fps 25 -t 86400000 -b 1100000 -o - | psips | ffmpeg -i - -an -c:v copy /capture/videos/" + formatted_date + ".mp4"
  recording_process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

def stop_recording():
  global recording, recording_process, formatted_date
  if not recording:
    return
  os.killpg(recording_process.pid, signal.SIGTERM)
  add_entry("FINALISING:"+formatted_date);
  print "Killed recording, ..."
  recording_process.wait()
  print "... done; generating thumbnail..."
  subprocess.call("ffmpeg -ss 10.0 -i /capture/videos/" + formatted_date + ".mp4 -f image2 -vframes 1 /capture/videos/" + formatted_date + ".png", shell = True)
  print "... done"
  recording = False
  add_entry("DONE:"+formatted_date)
  add_video(formatted_date)

add_entry("BOOT")
while True:
  if wiringpi2.digitalRead(MOTION_PIN):
    motionDetected = time()
    if time() - notified > 5:
      add_entry("MOTION")
      notified = time()

  if time() - motionDetected < 5:
    brightness += STEP
    if not recording:
      start_recording()
  else:
    brightness -= STEP

  if brightness < BRIGHTNESS_MIN:
    brightness = BRIGHTNESS_MIN
    if recording:
      stop_recording()
  if brightness > BRIGHTNESS_MAX:
    brightness = BRIGHTNESS_MAX

  if brightness != notifiedBrightness:
    add_entry("BRIGHTNESS:%d" % brightness)
    notifiedBrightness = brightness

  wiringpi2.pwmWrite(LED_PIN, brightness)

  sleep(1.0/FREQUENCY)
