#!/usr/bin/env python

# Copyright (c) 2019-2020, NVIDIA CORPORATION. All rights reserved.
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

from __future__ import print_function
import sys

import RPi.GPIO as GPIO

pin_datas = {
    'JETSON_XAVIER': {
        'unimplemented': (),
    },
    'JETSON_TX2': {
        'unimplemented': (26, ),
    },
    'JETSON_TX1': {
        'unimplemented': (),
    },
    'JETSON_NANO': {
        'unimplemented': (),
    },
    'JETSON_NX': {
        'unimplemented': (),
    },
    'CLARA_AGX_XAVIER': {
        'unimplemented': (),
    },
    'JETSON_TX2_NX': {
        'unimplemented': (),
    },
}
pin_data = pin_datas.get(GPIO.model)
all_pins = (7, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, 32, 33,
            35, 36, 37, 38, 40,)

if len(sys.argv) > 1:
    all_pins = map(int, sys.argv[1:])

for pin in all_pins:
    if pin in pin_data['unimplemented']:
        print("Pin %d unimplemented; skipping" % pin)
        continue

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.IN)
    value = GPIO.input(pin)
    print("Pin %d input value %d" % (pin, value))
    GPIO.cleanup()
