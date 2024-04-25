# bno055_test.py Simple test program for MicroPython bno055 driver

# Copyright (c) Peter Hinch 2019
# Released under the MIT licence.

import machine
import time
from bno055 import *
import urequests as requests
# Tested configurations
# Pyboard hardware I2C
# i2c = machine.I2C(1)

# Pico: hard I2C doesn't work without this patch
# https://github.com/micropython/micropython/issues/8167#issuecomment-1013696765
i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5))  # EIO error almost immediately

# All platforms: soft I2C requires timeout >= 1000μs
# i2c = machine.SoftI2C(sda=machine.Pin(16), scl=machine.Pin(17), timeout=1_000)
# ESP8266 soft I2C
# i2c = machine.SoftI2C(scl=machine.Pin(2), sda=machine.Pin(0), timeout=100_000)
# ESP32 hard I2C
# i2c = machine.I2C(1, scl=machine.Pin(21), sda=machine.Pin(23))


SERVER_ADDRESS = 'http://134.82.207.2:5025/receive_data'

def send_data(data):
    try:
        response = requests.post(SERVER_ADDRESS, json=data)
        print('data sent successfully', response.text)
    except Exception as e:
        print('Error sending data: ', e)
        time.sleep(10)


while True:
    try:
        imu = BNO055(i2c)
    except:
        print("error connecting")
        time.sleep(1)
        continue
    calibrated = False
    imu.mode(ACCGYRO_MODE)
    cfg = (2, 250)
    imu.config(ACC, cfg)
    if imu.config(ACC) == cfg:
        print("success!")
    while True:
        time.sleep(.05)
        if not calibrated:
            calibrated = imu.calibrated()
        print('Accel     x {:5.8f}    y {:5.8f}     z {:5.8f}'.format(*imu.accel()))
        accel_data = imu.accel()

        data = {'x': accel_data[0], 'y': accel_data[1], 'z': accel_data[2]}

        send_data(data)

        time.sleep(.1)

