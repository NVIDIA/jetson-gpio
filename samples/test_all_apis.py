#!/usr/bin/env python

# Copyright (c) 2019-2023, NVIDIA CORPORATION. All rights reserved.
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
import mmap
import os
import sys
import threading
import time
import warnings

import RPi.GPIO as GPIO

# If a board has PWM support, the PWM tests expect 'out_a' to be PWM-capable.
pin_datas = {
     'JETSON_ORIN_NANO': {
        # Pre-test configuration, if boot-time pinmux doesn't set up PWM pins:
        # Set BOARD pin 15 as mux function PWM:
        # busybox devmem 0x02440020 32 0x400
        # Set BOARD pin 33 as mux function PWM:
        # busybox devmem 0x02434040 32 0x401
        # Board mode pins
        'out_a': 33,
        'in_a': 19,
        'out_b': 11,
        'in_b': 13,
        'unimplemented_pins': (),
        # Other pin modes:
        'cvm_pin': 'GPIO09',
        'tegra_soc_pin': 'GP167',
        'all_pwms': (15, 33),
    },
     'JETSON_ORIN_NX': {
        # Pre-test configuration, if boot-time pinmux doesn't set up PWM pins:
        # Set BOARD pin 15 as mux function PWM:
        # busybox devmem 0x02440020 32 0x400
        # Set BOARD pin 33 as mux function PWM:
        # busybox devmem 0x02434040 32 0x401
        # Board mode pins
        'out_a': 33,
        'in_a': 19,
        'out_b': 11,
        'in_b': 13,
        'unimplemented_pins': (),
        # Other pin modes:
        'cvm_pin': 'GPIO09',
        'tegra_soc_pin': 'GP167',
        'all_pwms': (15, 33),
    },
     'JETSON_ORIN': {
        # Pre-test configuration, if boot-time pinmux doesn't set up PWM pins:
        # Set BOARD pin 15 as mux function PWM:
        # busybox devmem 0x02440020 32 0x400
        # Set BOARD pin 18 as mux function PWM:
        # busybox devmem 0x02434040 32 0x401
        # Board mode pins
        'out_a': 18,
        'in_a': 19,
        'out_b': 11,
        'in_b': 13,
        'unimplemented_pins': (),
        # Other pin modes:
        'cvm_pin': 'MCLK05',
        'tegra_soc_pin': 'GP66',
        'all_pwms': (15, 18),
    },
    'JETSON_XAVIER': {
        # Pre-test configuration, if boot-time pinmux doesn't set up PWM pins:
        # Set BOARD pin 18 as mux function PWM:
        # busybox devmem 0x2434090 32 0x401
        # Board mode pins
        'out_a': 18,
        'in_a': 19,
        'out_b': 21,
        'in_b': 22,
        'unimplemented_pins': (),
        # Other pin modes:
        'cvm_pin': 'MCLK05',
        'tegra_soc_pin': 'SOC_GPIO42',
        'all_pwms': (13, 15, 18),
    },
    'JETSON_TX2': {
        # Board mode pins
        'out_a': 18,
        'in_a': 19,
        'out_b': 21,
        'in_b': 22,
        'unimplemented_pins': (26,),
        # Other pin modes:
        'cvm_pin': 'AUDIO_MCLK',
        'tegra_soc_pin': 'AUD_MCLK',
    },
    'JETSON_TX1': {
        # Board mode pins
        'out_a': 18,
        'in_a': 19,
        'out_b': 21,
        'in_b': 22,
        'unimplemented_pins': (),
        # Other pin modes:
        'cvm_pin': 'AUDIO_MCLK',
        'tegra_soc_pin': 'AUD_MCLK',
    },
    'JETSON_NANO': {
        # Pre-test configuration, if boot-time pinmux doesn't set up PWM pins:
        # Set BOARD pin 32 as mux function PWM (set bits 1:0 to 1 not 3):
        # sudo busybox devmem 0x700031fc 32 0x45
        # Set BOARD pin 32 as SFIO (clear bit 0):
        # sudo busybox devmem 0x6000d504 32 0x2
        # Board mode pins
        'out_a': 32,
        'in_a': 31,
        'out_b': 29,
        'in_b': 26,
        'unimplemented_pins': (),
        # Other pin modes:
        'cvm_pin': 'GPIO9',
        'tegra_soc_pin': 'AUD_MCLK',
        'all_pwms': (32, 33),
    },
    'JETSON_NX': {
        # Pre-test configuration, if boot-time pinmux doesn't set up PWM pins:
        # Set BOARD pin 32 as mux function PWM (func 1):
        # busybox devmem 0x2430040 32 0x401
        # Set BOARD pin 33 as mux function PWM (func 2):
        # busybox devmem 0x2440020 32 0x402
        # Board mode pins
        'out_a': 32,
        'in_a': 31,
        'out_b': 29,
        'in_b': 26,
        'unimplemented_pins': (),
        # Other pin modes:
        'cvm_pin': 'GPIO09',
        'tegra_soc_pin': 'AUD_MCLK',
        'all_pwms': (15, 32, 33),
    },
    'CLARA_AGX_XAVIER': {
        # Pre-test configuration, if boot-time pinmux doesn't set up PWM pins:
        # Set BOARD pin 18 as mux function PWM:
        # busybox devmem 0x2434090 32 0x401
        # Board mode pins
        'out_a': 18,
        'in_a': 19,
        'out_b': 21,
        'in_b': 22,
        'unimplemented_pins': (),
        # Other pin modes:
        'cvm_pin': 'MCLK05',
        'tegra_soc_pin': 'SOC_GPIO42',
        'all_pwms': (15, 18),
    },
    'JETSON_TX2_NX': {
        # Pre-test configuration, if boot-time pinmux doesn't set up PWM pins:
        # Set BOARD pin 33 as mux function PWM (func 1):
        # busybox devmem 0x0c3010a8 32 0x401
        # Set BOARD pin 32 as mux function PWM (func 2):
        # busybox devmem 0x0c301080 32 0x401
        # Board mode pins
        'out_a': 32,
        'in_a': 31,
        'out_b': 29,
        'in_b': 26,
        'unimplemented_pins': (),
        # Other pin modes:
        'cvm_pin': 'GPIO09',
        'tegra_soc_pin': 'AUD_MCLK',
        'all_pwms': (32, 33),
    },
}
pin_data = pin_datas.get(GPIO.model)

# Board mode
all_board_pins = (7, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31,
                  32, 33, 35, 36, 37, 38, 40,)
bcm_pin = 4

tests = []


def test(f):
    tests.append(f)
    return f


def pwmtest(f):
    if pin_data.get('all_pwms', None):
        tests.append(f)
    return f


# Tests of:
# def setwarnings(state):

@test
def test_warnings_off():
    GPIO.setwarnings(False)
    with warnings.catch_warnings(record=True) as w:
        # cleanup() warns if no GPIOs were set up
        GPIO.cleanup()
    if len(w):
        raise Exception("Unexpected warning occured")


@test
def test_warnings_on():
    GPIO.setwarnings(True)
    with warnings.catch_warnings(record=True) as w:
        # cleanup() warns if no GPIOs were set up
        GPIO.cleanup()
    if not len(w):
        raise Exception("Expected warning did not occur")


# Tests of:
# def setmode(mode):
# def getmode():
# def setup(channels, direction, pull_up_down=PUD_OFF, initial=None):


@test
def test_setup_one_board():
    GPIO.setmode(GPIO.BOARD)
    assert GPIO.getmode() == GPIO.BOARD
    GPIO.setup(pin_data['in_a'], GPIO.IN)
    GPIO.cleanup()
    assert GPIO.getmode() is None


@test
def test_setup_one_bcm():
    GPIO.setmode(GPIO.BCM)
    assert GPIO.getmode() == GPIO.BCM
    GPIO.setup(bcm_pin, GPIO.IN)
    GPIO.cleanup()
    assert GPIO.getmode() is None


@test
def test_setup_one_cvm():
    GPIO.setmode(GPIO.CVM)
    assert GPIO.getmode() == GPIO.CVM
    GPIO.setup(pin_data['cvm_pin'], GPIO.IN)
    GPIO.cleanup()
    assert GPIO.getmode() is None


@test
def test_setup_one_tegra_soc():
    GPIO.setmode(GPIO.TEGRA_SOC)
    assert GPIO.getmode() == GPIO.TEGRA_SOC
    GPIO.setup(pin_data['tegra_soc_pin'], GPIO.IN)
    GPIO.cleanup()
    assert GPIO.getmode() is None

@test
def test_setup_twice():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)

    GPIO.setup(pin_data['in_a'], GPIO.IN)
    GPIO.setup(pin_data['in_a'], GPIO.IN)

    val = GPIO.input(pin_data['in_a'])
    assert(val == GPIO.HIGH)
    GPIO.cleanup()

@test
def test_setup_one_out_no_init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT)
    GPIO.cleanup()


@test
def test_setup_one_out_high():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)
    GPIO.cleanup()


@test
def test_setup_one_out_low():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.LOW)
    GPIO.cleanup()


@test
def test_setup_many_out_no_init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup((pin_data['out_a'], pin_data['out_b']), GPIO.OUT)
    GPIO.cleanup()


@test
def test_setup_many_out_one_init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup((pin_data['out_a'], pin_data['out_b']), GPIO.OUT,
               initial=GPIO.HIGH)
    GPIO.cleanup()


@test
def test_setup_many_out_many_init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup((pin_data['out_a'], pin_data['out_b']), GPIO.OUT,
               initial=(GPIO.HIGH, GPIO.HIGH))
    GPIO.cleanup()


@test
def test_setup_one_in():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['in_a'], GPIO.IN)
    GPIO.cleanup()


@test
def test_setup_one_in_pull():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['in_a'], GPIO.IN, GPIO.PUD_OFF)
    GPIO.cleanup()


@test
def test_setup_many_in():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup((pin_data['in_a'], pin_data['in_b']), GPIO.IN)
    GPIO.cleanup()


@test
def test_setup_all():
    GPIO.setmode(GPIO.BOARD)
    for pin in all_board_pins:
        if pin in pin_data['unimplemented_pins']:
            continue
        GPIO.setup(pin, GPIO.IN)
    GPIO.cleanup()


# Tests of:
# def cleanup(channel=None):
# def getmode():


@test
def test_cleanup_one():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['in_a'], GPIO.IN)
    GPIO.cleanup(pin_data['in_a'])
    assert GPIO.getmode() == GPIO.BOARD
    GPIO.cleanup()
    assert GPIO.getmode() is None


@test
def test_cleanup_many():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup((pin_data['in_a'], pin_data['in_b']), GPIO.IN)
    GPIO.cleanup((pin_data['in_a'], pin_data['in_b']))
    assert GPIO.getmode() == GPIO.BOARD
    GPIO.cleanup()
    assert GPIO.getmode() is None


@test
def test_cleanup_all():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup((pin_data['in_a'], pin_data['in_b']), GPIO.IN)
    GPIO.cleanup()
    assert GPIO.getmode() is None


# Tests of:
# def input(channel):


@test
def test_input():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['in_a'], GPIO.IN)
    GPIO.input(pin_data['in_a'])
    GPIO.cleanup()


# Tests of:
# def output(channels, values):


@test
def test_output_one():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT)
    GPIO.output(pin_data['out_a'], GPIO.HIGH)
    GPIO.output(pin_data['out_a'], GPIO.LOW)
    GPIO.cleanup()


@test
def test_output_many_one_value():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup((pin_data['out_a'], pin_data['out_b']), GPIO.OUT)
    GPIO.output((pin_data['out_a'], pin_data['out_b']), GPIO.HIGH)
    GPIO.output((pin_data['out_a'], pin_data['out_b']), GPIO.LOW)
    GPIO.cleanup()


@test
def test_output_many_many_value():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup((pin_data['out_a'], pin_data['out_b']), GPIO.OUT)
    GPIO.output((pin_data['out_a'], pin_data['out_b']), (GPIO.HIGH, GPIO.LOW))
    GPIO.output((pin_data['out_a'], pin_data['out_b']), (GPIO.LOW, GPIO.HIGH))
    GPIO.cleanup()


# Tests of combined (looped back) output/input


@test
def test_out_in_init_high():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(pin_data['in_a'], GPIO.IN)
    val = GPIO.input(pin_data['in_a'])
    assert(val == GPIO.HIGH)
    GPIO.output(pin_data['out_a'], GPIO.LOW)
    val = GPIO.input(pin_data['in_a'])
    assert(val == GPIO.LOW)
    GPIO.output(pin_data['out_a'], GPIO.HIGH)
    val = GPIO.input(pin_data['in_a'])
    assert(val == GPIO.HIGH)
    GPIO.cleanup()


@test
def test_out_in_init_low():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_data['in_a'], GPIO.IN)
    val = GPIO.input(pin_data['in_a'])
    assert(val == GPIO.LOW)
    GPIO.output(pin_data['out_a'], GPIO.HIGH)
    val = GPIO.input(pin_data['in_a'])
    assert(val == GPIO.HIGH)
    GPIO.output(pin_data['out_a'], GPIO.LOW)
    val = GPIO.input(pin_data['in_a'])
    assert(val == GPIO.LOW)
    GPIO.cleanup()


# Tests of:
# def gpio_function(channel):


@test
def test_gpio_function_unexported():
    GPIO.setmode(GPIO.BOARD)
    val = GPIO.gpio_function(pin_data['in_a'])
    assert val == GPIO.UNKNOWN
    GPIO.cleanup()


@test
def test_gpio_function_in():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['in_a'], GPIO.IN)
    val = GPIO.gpio_function(pin_data['in_a'])
    assert val == GPIO.IN
    GPIO.cleanup()


@test
def test_gpio_function_out():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT)
    val = GPIO.gpio_function(pin_data['out_a'])
    assert val == GPIO.OUT
    GPIO.cleanup()


# Tests of:
# def wait_for_edge(channel, edge, bouncetime=None, timeout=None):


@test
def test_wait_for_edge_timeout():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_data['in_a'], GPIO.IN)
    for i in range(3):
        val = GPIO.wait_for_edge(pin_data['in_a'], GPIO.BOTH, timeout=1)
        assert val is None
    GPIO.cleanup()


class DelayedSetChannel(threading.Thread):
    def __init__(self, channel, value, delay):
        super(DelayedSetChannel, self).__init__()
        self.channel = channel
        self.value = value
        self.delay = delay

    def run(self):
        time.sleep(self.delay)
        GPIO.output(self.channel, self.value)


@test
def test_wait_for_edge_rising():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(pin_data['in_a'], GPIO.IN)
    dsc = DelayedSetChannel(pin_data['out_a'], GPIO.HIGH, 0.5)
    dsc.start()
    val = GPIO.wait_for_edge(pin_data['in_a'], GPIO.RISING, timeout=10)
    dsc.join()
    assert val == pin_data['in_a']
    GPIO.cleanup()


@test
def test_wait_for_edge_falling():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(pin_data['in_a'], GPIO.IN)
    dsc = DelayedSetChannel(pin_data['out_a'], GPIO.LOW, 0.5)
    dsc.start()
    val = GPIO.wait_for_edge(pin_data['in_a'], GPIO.FALLING, timeout=10)
    dsc.join()
    assert val == pin_data['in_a']
    GPIO.cleanup()


# Tests of:
# def add_event_detect(channel, edge, callback=None, bouncetime=None):
# def event_detected(channel):
# def add_event_callback(channel, callback):
# def remove_event_detect(channel):


def _test_events(init, edge, tests, specify_callback, use_add_callback):
    global event_callback_occurred
    event_callback_occurred = False

    # This is set as 0.5 sec delay because default remove event time is 0.5
    time.sleep(0.5)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=init)
    GPIO.setup(pin_data['in_a'], GPIO.IN)

    def callback(channel):
        global event_callback_occurred
        if channel != pin_data['in_a']:
            return
        event_callback_occurred = True

    def get_saw_event():
        global event_callback_occurred
        if specify_callback or use_add_callback:
            val = event_callback_occurred
            event_callback_occurred = False
            return val
        else:
            return GPIO.event_detected(pin_data['in_a'])

    if specify_callback:
        args = {'callback': callback, 'polltime': 0.2}
    else:
        args = {'polltime': 0.2}

    # After every pin state change, it is suggested to leave a time for the
    # pin to setup itself. Here, we are using 0.2 seconds to make sure the pin
    # state is stabilize. (Same reason as the following wait time after setting
    # the output pin)
    time.sleep(0.2)
    # By default, the poll time is also 0.2 seconds. the poll time should be set
    # to a large enough number to ensure the efficiency of thread, but also small
    # enough so that it can respond to the event removal as fast as possible.
    GPIO.add_event_detect(pin_data['in_a'], edge, **args)
    if use_add_callback:
        GPIO.add_event_callback(pin_data['in_a'], callback)

    assert not get_saw_event()

    for output, event_expected in tests:
        GPIO.output(pin_data['out_a'], output)
        time.sleep(0.2)
        assert get_saw_event() == event_expected
        assert not get_saw_event()

    # By default, the timeout for removal is also 0.5 seconds
    # The removal time should always be longer than the polltime, and it is
    # suggested to be two times greater. Thus, in this example, as the poll
    # time is set to 0.2, the timeout must be greater than 0.4.
    GPIO.remove_event_detect(pin_data['in_a'], timeout=0.5)
    GPIO.cleanup()


@test
def test_event_detected_falling():
    _test_events(
        GPIO.HIGH,
        GPIO.FALLING,
        (
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
        ),
        False,
        False
    )
    _test_events(
        GPIO.LOW,
        GPIO.FALLING,
        (
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
        ),
        True,
        False
    )


@test
def test_event_detected_rising():
    _test_events(
        GPIO.HIGH,
        GPIO.RISING,
        (
            (GPIO.LOW, False),
            (GPIO.HIGH, True),
            (GPIO.LOW, False),
            (GPIO.HIGH, True),
        ),
        False,
        False
    )
    _test_events(
        GPIO.LOW,
        GPIO.RISING,
        (
            (GPIO.HIGH, True),
            (GPIO.LOW, False),
            (GPIO.HIGH, True),
            (GPIO.LOW, False),
        ),
        True,
        False
    )


@test
def test_event_detected_both():
    _test_events(
        GPIO.HIGH,
        GPIO.BOTH,
        (
            (GPIO.LOW, True),
            (GPIO.HIGH, True),
            (GPIO.LOW, True),
            (GPIO.HIGH, True),
        ),
        False,
        False
    )
    _test_events(
        GPIO.LOW,
        GPIO.BOTH,
        (
            (GPIO.HIGH, True),
            (GPIO.LOW, True),
            (GPIO.HIGH, True),
            (GPIO.LOW, True),
        ),
        False,
        True
    )

# Tests of multiple:
# def add_event_callback(channel, callback):

def _test_callbacks(init, edge, tests, specify_callback, use_add_callback):
    global event_callback_occurred
    global event_callback_occurred_2
    event_callback_occurred = False
    event_callback_occurred_2 = False

    # This is set as 0.5 sec delay because default remove event time is 0.5
    time.sleep(0.5)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=init)
    GPIO.setup(pin_data['in_a'], GPIO.IN)

    def callback(channel):
        global event_callback_occurred
        if channel != pin_data['in_a']:
            return
        event_callback_occurred = True

    def callback2(channel):
        global event_callback_occurred_2
        if channel != pin_data['in_a']:
            return
        event_callback_occurred_2 = True

    # return true if every event has been detected
    def get_saw_event():
        global event_callback_occurred
        global event_callback_occurred_2
        if specify_callback:
            val = event_callback_occurred
            event_callback_occurred = False
            return val
        elif use_add_callback:
            val = event_callback_occurred and event_callback_occurred_2
            event_callback_occurred = False
            event_callback_occurred_2 = False
            return val
        else:
            return GPIO.event_detected(pin_data['in_a'])

    # return true if every event has not been detected
    # if any one event occurs, it will return false
    def not_get_saw_event():
        global event_callback_occurred
        global event_callback_occurred_2
        if specify_callback:
            val = event_callback_occurred
            event_callback_occurred = False
            return not val
        elif use_add_callback:
            val = event_callback_occurred or event_callback_occurred_2
            event_callback_occurred = False
            event_callback_occurred_2 = False
            return not val
        else:
            return not GPIO.event_detected(pin_data['in_a'])

    if specify_callback:
        args = {'callback': callback, 'polltime': 0.2}
    else:
        args = {'polltime': 0.2}

    time.sleep(0.2)

    GPIO.add_event_detect(pin_data['in_a'], edge, **args)
    if use_add_callback:
        # adding double callback functions
        GPIO.add_event_callback(pin_data['in_a'], callback)
        GPIO.add_event_callback(pin_data['in_a'], callback2)

    assert not_get_saw_event()

    for output, event_expected in tests:
        GPIO.output(pin_data['out_a'], output)
        time.sleep(0.2)
        assert get_saw_event() == event_expected
        assert not_get_saw_event()

    GPIO.remove_event_detect(pin_data['in_a'], timeout=0.5)
    GPIO.cleanup()


@test
def test_event_callbacks():
    _test_callbacks(
        GPIO.HIGH,
        GPIO.FALLING,
        (
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
        ),
        False,
        True
    )
    _test_callbacks(
        GPIO.LOW,
        GPIO.FALLING,
        (
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
        ),
        True,
        False
    )
    _test_callbacks(
        GPIO.LOW,
        GPIO.FALLING,
        (
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
        ),
        False,
        True
    )

# Tests of multiple events at a time:

def _test_multi_events(init_a, edge_a, tests_a, init_b, edge_b, tests_b, specify_callback):
    event_dict = { 'series_a': {'in_pin_name': 'in_a',
                                'out_pin_name': 'out_a',
                                'event_callback_occurred': False,
                                'init': init_a,
                                'edge': edge_a,
                                'tests': tests_a},
                   'series_b': {'in_pin_name': 'in_b',
                                'out_pin_name': 'out_b',
                                'event_callback_occurred': False,
                                'init': init_b,
                                'edge': edge_b,
                                'tests': tests_b}}
    test_number = len(tests_a)

    # internal functions
    def callback(channel):
        for pin_series in event_dict.keys():
            input_pin_name = event_dict[pin_series]['in_pin_name']

            if channel == pin_data[input_pin_name]:
                event_dict[pin_series]['event_callback_occurred'] = True

                return

    def get_saw_event(series_name):
        if specify_callback:
            val = event_dict[series_name]['event_callback_occurred']
            event_dict[series_name]['event_callback_occurred'] = False
            return val
        else:
            pin_name = event_dict[series_name]['in_pin_name']
            return GPIO.event_detected(pin_data[pin_name])

    # setup
    time.sleep(0.5)
    GPIO.setmode(GPIO.BOARD)
    for pin_series in event_dict.keys():
        input_pin_name = event_dict[pin_series]['in_pin_name']
        output_pin_name = event_dict[pin_series]['out_pin_name']

        GPIO.setup(pin_data[output_pin_name], GPIO.OUT, initial=event_dict[pin_series]['init'])
        GPIO.setup(pin_data[input_pin_name], GPIO.IN)

        if specify_callback:
            args = {'callback': callback, 'polltime': 0.2}
        else:
            args = {'polltime': 0.2}

        time.sleep(0.2)
        GPIO.add_event_detect(pin_data[input_pin_name], event_dict[pin_series]['edge'], **args)

        assert not get_saw_event(pin_series)

    # test edges
    index=0
    while index < test_number:
        for pin_series in event_dict.keys():
            output_pin_name = event_dict[pin_series]['out_pin_name']
            input_pin_name = event_dict[pin_series]['in_pin_name']
            pin_tests = event_dict[pin_series]['tests']

            output, event_expected = pin_tests[index]

            GPIO.output(pin_data[output_pin_name], output)
            time.sleep(0.2)
            assert get_saw_event(pin_series) == event_expected
            assert not get_saw_event(pin_series)

        index += 1

    # cleanup
    for pin_series in event_dict.keys():
        input_pin_name = event_dict[pin_series]['in_pin_name']
        GPIO.remove_event_detect(pin_data[input_pin_name], timeout=0.5)
    GPIO.cleanup()


@test
def test_multi_events_detected_diff_edge():
    _test_multi_events(
        # series a
        GPIO.HIGH,
        GPIO.FALLING,
        (
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
        ),
        # series b
        GPIO.HIGH,
        GPIO.RISING,
        (
            (GPIO.LOW, False),
            (GPIO.HIGH, True),
            (GPIO.LOW, False),
            (GPIO.HIGH, True),
        ),
        False
    )
    _test_multi_events(
        GPIO.LOW,
        GPIO.FALLING,
        (
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
        ),
        GPIO.LOW,
        GPIO.RISING,
        (
            (GPIO.HIGH, True),
            (GPIO.LOW, False),
            (GPIO.HIGH, True),
            (GPIO.LOW, False),
        ),
        True
    )

@test
def test_multi_events_detected_same_edge():
    _test_multi_events(
        # series a
        GPIO.HIGH,
        GPIO.FALLING,
        (
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
        ),
        # series b
        GPIO.HIGH,
        GPIO.FALLING,
        (
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
        ),
        False
    )
    _test_multi_events(
        GPIO.LOW,
        GPIO.FALLING,
        (
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
        ),
        GPIO.HIGH,
        GPIO.FALLING,
        (
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
            (GPIO.LOW, True),
            (GPIO.HIGH, False),
        ),
        True
    )

# Tests of pinmux check warnings

@test
def test_orin_nano_nx_pinmux_warnings():
    if GPIO.model != 'JETSON_ORIN_NANO' and GPIO.model != 'JETSON_ORIN_NX':
        return
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(True)
    mem_fd = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
    # These depend on the pin being BCM 4 for Orin nano/nx
    PIN_REGISTER_ADDR = 0x02448000 + 0x28
    REG_PAGE_START = PIN_REGISTER_ADDR & ~(mmap.PAGESIZE - 1)
    REG_PAGE_OFFSET = PIN_REGISTER_ADDR - REG_PAGE_START
    GPIO_INPUT_BITS = 0b1010100
    GPIO_OUTPUT_BITS = 0b0000100
    GPIO_BIDI_BITS = 0b1000100

    with warnings.catch_warnings(record=True) as w:
        with mmap.mmap(mem_fd, length=mmap.PAGESIZE * 2, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ | mmap.PROT_WRITE, offset=REG_PAGE_START) as devmem:
            # Set pinmux to input
            devmem.seek(REG_PAGE_OFFSET)
            devmem.write(GPIO_INPUT_BITS.to_bytes(4, sys.byteorder))
            # Should produce no warnings
            GPIO.setup(bcm_pin, GPIO.IN)
            GPIO.cleanup(bcm_pin)
            # Should produce 1 warning
            GPIO.setup(bcm_pin, GPIO.OUT, initial=GPIO.LOW)
            GPIO.cleanup(bcm_pin)

            # Set pinmux to output
            devmem.seek(REG_PAGE_OFFSET)
            devmem.write(GPIO_OUTPUT_BITS.to_bytes(4, sys.byteorder))
            # Should produce 1 warning
            GPIO.setup(bcm_pin, GPIO.IN)
            GPIO.cleanup(bcm_pin)
            # Should produce no warnings
            GPIO.setup(bcm_pin, GPIO.OUT, initial=GPIO.LOW)
            GPIO.cleanup(bcm_pin)

            # Set pinmux to bi-direcrtional
            devmem.seek(REG_PAGE_OFFSET)
            devmem.write(GPIO_BIDI_BITS.to_bytes(4, sys.byteorder))
            # Should produce no warnings
            GPIO.setup(bcm_pin, GPIO.IN)
            GPIO.cleanup(bcm_pin)
            # Should produce no warnings
            GPIO.setup(bcm_pin, GPIO.OUT, initial=GPIO.LOW)
            GPIO.cleanup(bcm_pin)

        if len(w) != 2:
            raise Exception(f"Unexpected warnings occured: {w}")
        

# Tests of class PWM


@pwmtest
def test_pwm_multi_duty():
    for pct in (25, 50, 75):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin_data['in_a'], GPIO.IN)
        GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)
        p = GPIO.PWM(pin_data['out_a'], 500)
        p.start(pct)
        count = 0
        for i in range(1000):
            count += GPIO.input(pin_data['in_a'])
        p.stop()
        del p
        min_ct = 10 * (pct - 5)
        max_ct = 10 * (pct + 5)
        assert min_ct <= count <= max_ct
        GPIO.cleanup()


@pwmtest
def test_pwm_change_frequency():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(pin_data['out_a'], 500)
    p.start(50)
    p.ChangeFrequency(550)
    p.stop()
    del p
    GPIO.cleanup()


@pwmtest
def test_pwm_change_duty_cycle():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(pin_data['out_a'], 500)
    p.start(50)
    p.ChangeDutyCycle(60)
    p.stop()
    del p
    GPIO.cleanup()


@pwmtest
def test_pwm_cleanup_none():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(pin_data['out_a'], 500)
    p.start(50)
    GPIO.cleanup()


@pwmtest
def test_pwm_cleanup_stop():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(pin_data['out_a'], 500)
    p.start(50)
    p.stop()
    GPIO.cleanup()


@pwmtest
def test_pwm_cleanup_del():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_data['out_a'], GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(pin_data['out_a'], 500)
    p.start(50)
    del p
    GPIO.cleanup()


@pwmtest
def test_pwm_create_all():
    for pin in pin_data['all_pwms']:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
        p = GPIO.PWM(pin, 500)
        p.start(50)
        p.stop()
        GPIO.cleanup()


# Main script


if __name__ == '__main__':
    for test in tests:
        print('Testing', test.__name__)
        try:
            test()
        except:
            # This isn't a finally block, since we don't want to repeat the
            # cleanup() call that a successful test already made.
            GPIO.cleanup()
            raise
