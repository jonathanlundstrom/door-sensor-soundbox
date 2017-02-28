#!/usr/bin/python
#
# sensor.py
# Detect when door has been opened and play random audio from soundpack.
# The code is very straight forward and should be self explanatory.
# If need of assistance, use the email address provided below.
#
# Date:      11/02/2017
# Author:    Jonathan Lundstrom
# Website:   http://jonathanlundstrom.me
# Email:     contact@jonathanlundstrom.me

import time
import random
import pygame
import os.path
import ConfigParser
import RPi.GPIO as GPIO

config = ConfigParser.ConfigParser()
config_path = os.path.realpath(__file__).replace(__file__, "config.ini")
config.read(config_path)

pygame.mixer.init()
pygame.mixer.fadeout(config.getint("Audio", "fadeout"))
pygame.mixer.music.set_volume(config.getfloat("Audio", "volume"))

current_state = 0
previous_state = 0
sensor_pin = config.getint("General", "gpio_pin")
soundpack_path = "soundpacks/%s" % config.get("Audio", "soundpack")

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def reloadConfig():
  config.read(config_path)
  pygame.mixer.fadeout(config.getint("Audio", "fadeout"))
  pygame.mixer.music.set_volume(config.getfloat("Audio", "volume"))
  return "soundpacks/%s" % config.get("Audio", "soundpack")

def playAudioClip(path):
  pygame.mixer.music.load(path)
  pygame.mixer.music.play()
  while pygame.mixer.music.get_busy() == True:
    continue

if config.getboolean("Features", "sound_on_start"):
  playAudioClip("features/start_sound.wav")

try:
  print "Waiting for door to open for the first time..."
  while GPIO.input(sensor_pin) == 1:
    current_state = 0;

  while True:
    current_state = GPIO.input(sensor_pin)
    if current_state == 1 and previous_state == 0:
      print "Door has been opened"
      soundpack_path = reloadConfig()

      if os.path.isdir(soundpack_path):
        playAudioClip("%s/%s" % (soundpack_path, random.choice(os.listdir(soundpack_path))))
      else:
        print "Selected soundpack does not exist, please fix this and restart."
        playAudioClip("features/error.wav")
      previous_state = 1
    elif current_state == 0 and previous_state == 1:
      previous_state = 0
    
    time.sleep(0.01)

except KeyboardInterrupt:
  print " Hasta la vista, baby!"
  GPIO.cleanup()

  if config.getboolean("Features", "sound_on_exit"):
    playAudioClip("features/exit_sound.wav")