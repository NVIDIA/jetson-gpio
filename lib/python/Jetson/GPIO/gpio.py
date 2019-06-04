# Copyright (c) 2012-2017 Ben Croston <ben@croston.org>.
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
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

from Jetson.GPIO import gpio_event as event
from Jetson.GPIO import gpio_pin_data
import os
import time
import warnings

# sysfs root
_SYSFS_ROOT = "/sys/class/gpio"

if (not os.access(_SYSFS_ROOT + '/export', os.W_OK) or
        not os.access(_SYSFS_ROOT + '/unexport', os.W_OK)):
    raise RuntimeError("The current user does not have permissions set to "
                       "access the library functionalites. Please configure "
                       "permissions or use the root user to run this")

# Pin Numbering Modes
BOARD = 10
BCM = 11
TEGRA_SOC = 1000
CVM = 1001

# The constants and their offsets are implemented to prevent HIGH from being
# used in place of other variables (ie. HIGH and RISING should not be
# interchangeable)

# Pull up/down options
_PUD_OFFSET = 20
PUD_OFF = 0 + _PUD_OFFSET
PUD_DOWN = 1 + _PUD_OFFSET
PUD_UP = 2 + _PUD_OFFSET

HIGH = 1
LOW = 0

# Edge possibilities
# These values (with _EDGE_OFFSET subtracted) must match gpio_event.py:*_EDGE
_EDGE_OFFSET = 30
RISING = 1 + _EDGE_OFFSET
FALLING = 2 + _EDGE_OFFSET
BOTH = 3 + _EDGE_OFFSET

# GPIO directions. UNKNOWN constant is for gpios that are not yet setup
UNKNOWN = -1
OUT = 0
IN = 1


JETSON_INFO, _pin_mapping = gpio_pin_data.get_data()
RPI_INFO = JETSON_INFO

# Dictionary objects used as lookup tables for pin to linux gpio mapping
_pin_to_gpio = {}

_gpio_warnings = True
_gpio_mode = None
_channel_configuration = {}


def _validate_mode_set():
    if _gpio_mode is None:
        raise RuntimeError("Please set pin numbering mode using "
                           "GPIO.setmode(GPIO.BOARD), GPIO.setmode(GPIO.BCM), "
                           "GPIO.setmode(GPIO.TEGRA_SOC) or "
                           "GPIO.setmode(GPIO.CVM)")


def _make_iterable(iterable, single_length=None):
    if isinstance(iterable, str):
        iterable = [iterable]
    try:
        for x in iterable:
            break
    except:
        iterable = [iterable]
    if single_length is not None and len(iterable) == 1:
        iterable = iterable * single_length
    return iterable


def _channel_to_gpio(channel):
    if channel not in _pin_to_gpio or _pin_to_gpio[channel][0] is None:
        raise ValueError("Channel %s is invalid" % str(channel))
    return _pin_to_gpio[channel][2]


def _channel_to_gpio_single(channel):
    _validate_mode_set()
    return _channel_to_gpio(channel)


def _channels_to_gpio_list(channels):
    _validate_mode_set()
    return [_channel_to_gpio(c) for c in channels]


def _check_pin_setup(channel):
    return _channel_configuration.get(channel, None)


def _export_gpio(gpio):
    if os.path.exists(_SYSFS_ROOT + "/gpio%i" % gpio):
        return

    with open(_SYSFS_ROOT + "/export", "w") as f_export:
        f_export.write(str(gpio))

    while not os.access(_SYSFS_ROOT + "/gpio%i" % gpio + "/direction",
                        os.R_OK | os.W_OK):
        time.sleep(0.01)


def _unexport_gpio(gpio):
    if not os.path.exists(_SYSFS_ROOT + "/gpio%i" % gpio):
        return

    with open(_SYSFS_ROOT + "/unexport", "w") as f_unexport:
        f_unexport.write(str(gpio))


def _output_one(gpio, value):
    with open(_SYSFS_ROOT + "/gpio%s" % gpio + "/value", 'w') as value_file:
        value_file.write(str(int(bool(value))))


# Function used to check the currently set function of the channel specified.
# Param channel must be an integers. The function returns either IN, OUT,
# or UNKNOWN
def _gpio_function(channel, gpio):
    gpio_dir = _SYSFS_ROOT + "/gpio%i" % gpio

    if not os.path.exists(gpio_dir):
        return UNKNOWN

    with open(gpio_dir + "/direction", 'r') as f_direction:
        function_ = f_direction.read()

    return function_.rstrip()


def _setup_single_out(channel, gpio, initial=None):
    _export_gpio(gpio)

    gpio_dir_path = _SYSFS_ROOT + "/gpio%i" % gpio + "/direction"
    with open(gpio_dir_path, 'w') as direction_file:
        direction_file.write("out")

    if initial is not None:
        _output_one(gpio, initial)

    _channel_configuration[channel] = OUT


def _setup_single_in(channel, gpio):
    _export_gpio(gpio)

    gpio_dir_path = _SYSFS_ROOT + "/gpio%i" % gpio + "/direction"
    with open(gpio_dir_path, 'w') as direction:
        direction.write("in")

    _channel_configuration[channel] = IN


def _cleanup_one(channel, gpio):
    del _channel_configuration[channel]
    event.event_cleanup(gpio)
    _unexport_gpio(gpio)


def _cleanup_all():
    global _gpio_mode

    for channel in list(_channel_configuration.keys()):
        gpio = _channel_to_gpio(channel)
        _cleanup_one(channel, gpio)

    _gpio_mode = None


# Function used to enable/disable warnings during setup and cleanup.
# Param -> state is a bool
def setwarnings(state):
    global _gpio_warnings
    _gpio_warnings = bool(state)


# Function used to set the pin mumbering mode. Possible mode values are BOARD,
# BCM, TEGRA_SOC and CVM
def setmode(mode):
    global _gpio_mode, _pin_to_gpio

    # check if a different mode has been set
    if _gpio_mode and mode != _gpio_mode:
        raise ValueError("A different mode has already been set!")

    mode_map = {
        BOARD: 'BOARD',
        BCM: 'BCM',
        CVM: 'CVM',
        TEGRA_SOC: 'TEGRA_SOC',
    }

    # check if mode parameter is valid
    if mode not in mode_map:
        raise ValueError("An invalid mode was passed to setmode()!")

    _pin_to_gpio = _pin_mapping[mode_map[mode]]
    _gpio_mode = mode


# Function used to get the currently set pin numbering mode
def getmode():
    return _gpio_mode


# Function used to setup individual pins or lists/tuples of pins as
# Input or Output. Param channels must an integer or list/tuple of integers,
# direction must be IN or OUT, pull_up_down must be PUD_OFF, PUD_UP or
# PUD_DOWN and is only valid when direction in IN, initial must be HIGH or LOW
# and is only valid when direction is OUT
def setup(channels, direction, pull_up_down=PUD_OFF, initial=None):
    channels = _make_iterable(channels)
    gpios = _channels_to_gpio_list(channels)

    # check direction is valid
    if direction != OUT and direction != IN:
        raise ValueError("An invalid direction was passed to setup()")

    # check if pullup/down is used with output
    if direction == OUT and pull_up_down != PUD_OFF:
        raise ValueError("pull_up_down parameter is not valid for outputs")

    # check if pullup/down value is valid
    if (pull_up_down != PUD_OFF and pull_up_down != PUD_UP and
            pull_up_down != PUD_DOWN):
        raise ValueError("Invalid value for pull_up_down - should be either"
                         "PUD_OFF, PUD_UP or PUD_DOWN")

    if _gpio_warnings:
        for channel, gpio in zip(channels, gpios):
            func = _gpio_function(channel, gpio)
            direction = _check_pin_setup(channel)

            # warn if channel has been setup external to current program
            if direction is None and func is not None:
                warnings.warn(
                    "This channel is already in use, continuing anyway. "
                    "Use GPIO.setwarnings(False) to disable warnings",
                    RuntimeWarning)

    if direction == OUT:
        initial = _make_iterable(initial, len(channels))
        if len(initial) != len(gpios):
            raise RuntimeError("Number of values != number of channels")
        for channel, gpio, init in zip(channels, gpios, initial):
            _setup_single_out(channel, gpio, init)
    else:
        if initial is not None:
            raise ValueError("initial parameter is not valid for inputs")
        for channel, gpio in zip(channels, gpios):
            _setup_single_in(channel, gpio)


# Function used to cleanup channels at the end of the program.
# The param channel can be an integer or list/tuple of integers specifying the
# channels to be cleaned up. If no channel is provided, all channels are
# cleaned
def cleanup(channel=None):
    # warn if no channel is setup
    if _gpio_mode is None:
        if _gpio_warnings:
            warnings.warn("No channels have been set up yet - nothing to "
                          "clean up! Try cleaning up at the end of your "
                          "program instead!", RuntimeWarning)
        return

    # clean all channels if no channel param provided
    if channel is None:
        _cleanup_all()
        return

    channels = _make_iterable(channel)
    gpios = _channels_to_gpio_list(channels)

    for channel, gpio in zip(channels, gpios):
        if channel in _channel_configuration:
            _cleanup_one(channel, gpio)


# Function used to return the current value of the specified channel.
# Function returns either HIGH or LOW
def input(channel):
    gpio = _channel_to_gpio_single(channel)

    direction = _check_pin_setup(channel)
    if direction != IN and direction != OUT:
        raise RuntimeError("You must setup() the GPIO channel first")

    with open(_SYSFS_ROOT + "/gpio%i" % gpio + "/value") as value:
        value_read = int(value.read())
        return value_read


# Function used to set a value to a channel or list/tuple of channels.
# Parameter channels must be an integer or list/tuple of integers.
# Values must be either HIGH or LOW or list/tuple
# of HIGH and LOW with the same length as the channels list/tuple
def output(channels, values):
    channels = _make_iterable(channels)
    gpios = _channels_to_gpio_list(channels)
    values = _make_iterable(values, len(channels))
    if len(values) != len(channels):
        raise RuntimeError("Number of values != number of channels")

    # check that channels have been set as output
    if any((_check_pin_setup(channel) != OUT) for channel in channels):
        raise RuntimeError("The GPIO channel has not been set up as an "
                           "OUTPUT")

    for gpio, value in zip(gpios, values):
        _output_one(gpio, value)


# Function used to check if an event occurred on the specified channel.
# Param channel must be an integer.
# This function return True or False
def event_detected(channel):
    gpio = _channel_to_gpio_single(channel)
    return event.edge_event_detected(gpio)


# Function used to add a callback function to channel, after it has been
# registered for events using add_event_detect()
def add_event_callback(channel, callback):
    gpio = _channel_to_gpio_single(channel)
    if not callable(callback):
        raise TypeError("Parameter must be callable")

    if _check_pin_setup(channel) != IN:
        raise RuntimeError("You must setup() the GPIO channel as an "
                           "input first")

    if not event.gpio_event_added(gpio):
        raise RuntimeError("Add event detection using add_event_detect first "
                           "before adding a callback")

    event.add_edge_callback(gpio, lambda: callback(channel))


# Function used to add threaded event detection for a specified gpio channel.
# Param gpio must be an integer specifying the channel, edge must be RISING,
# FALLING or BOTH. A callback function to be called when the event is detected
# and an integer bounctime in milliseconds can be optionally provided
def add_event_detect(channel, edge, callback=None, bouncetime=None):
    gpio = _channel_to_gpio_single(channel)
    if (not callable(callback)) and callback is not None:
        raise TypeError("Callback Parameter must be callable")

    # channel must be setup as input
    if _check_pin_setup(channel) != IN:
        raise RuntimeError("You must setup() the GPIO channel as an input "
                           "first")

    # edge must be rising, falling or both
    if edge != RISING and edge != FALLING and edge != BOTH:
        raise ValueError("The edge must be set to RISING, FALLING, or BOTH")

    # if bouncetime is provided, it must be int and greater than 0
    if bouncetime is not None:
        if type(bouncetime) != int:
            raise TypeError("bouncetime must be an integer")

        elif bouncetime < 0:
            raise ValueError("bouncetime must be an integer greater than 0")

    result = event.add_edge_detect(gpio, edge - _EDGE_OFFSET, bouncetime)

    # result == 1 means a different edge was already added for the channel.
    # result == 2 means error occurred while adding edge (thread or event poll)
    if result:
        error_str = None
        if result == 1:
            error_str = "Conflicting edge already enabled for this GPIO " + \
                        "channel"
        else:
            error_str = "Failed to add edge detection"

        raise RuntimeError(error_str)

    if callback is not None:
        event.add_edge_callback(gpio, lambda: callback(channel))


# Function used to remove event detection for channel
def remove_event_detect(channel):
    gpio = _channel_to_gpio_single(channel)
    event.remove_edge_detect(gpio)


# Function used to perform a blocking wait until the specified edge
# is detected for the param channel. Channel must be an integer and edge must
# be either RISING, FALLING or BOTH.
# bouncetime in milliseconds and timeout in millseconds can optionally be
# provided
def wait_for_edge(channel, edge, bouncetime=None, timeout=None):
    gpio = _channel_to_gpio_single(channel)

    # channel must be setup as input
    if _check_pin_setup(channel) != IN:
        raise RuntimeError("You must setup() the GPIO channel as an input "
                           "first")

    # edge provided must be rising, falling or both
    if edge != RISING and edge != FALLING and edge != BOTH:
        raise ValueError("The edge must be set to RISING, FALLING_EDGE "
                         "or BOTH")

    # if bouncetime is provided, it must be int and greater than 0
    if bouncetime is not None:
        if type(bouncetime) != int:
            raise TypeError("bouncetime must be an integer")

        elif bouncetime < 0:
            raise ValueError("bouncetime must be an integer greater than 0")

    # if timeout is specified, it must be an int and greater than 0
    if timeout is not None:
        if type(timeout) != int:
            raise TypeError("Timeout must be an integer")

        elif timeout < 0:
            raise ValueError("Timeout must greater than 0")

    result = event.blocking_wait_for_edge(gpio, edge - _EDGE_OFFSET,
                                          bouncetime, timeout)

    # If not error, result == channel. If timeout occurs while waiting,
    # result == None. If error occurs, result == -1 means channel is
    # registered for conflicting edge detection, result == -2 means an error
    # occurred while registering event or polling
    if not result:
        return None
    elif result == -1:
        raise RuntimeError("Conflicting edge detection event already exists "
                           "for this GPIO channel")

    elif result == -2:
        raise RuntimeError("Error waiting for edge")

    else:
        return channel


# Function used to check the currently set function of the channel specified.
# Param channel must be an integers. The function returns either IN, OUT,
# or UNKNOWN
def gpio_function(channel):
    gpio = _channel_to_gpio_single(channel)
    return _gpio_function(channel, gpio)
