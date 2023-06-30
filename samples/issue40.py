#!/usr/bin/env python

# Copyright (c) 2019-2022, NVIDIA CORPORATION. All rights reserved.
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import RPi.GPIO as GPIO
import time

pin = 31

def on_falling(channel):
    print("Callback.")

def main():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.IN)

    # By default, the poll time is 0.2 seconds, too
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=on_falling, bouncetime=300, polltime=0.2)
    print("Starting demo now! Press CTRL+C to exit")
    try:
        while True:
            print("Main loop...")
            time.sleep(5)
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
