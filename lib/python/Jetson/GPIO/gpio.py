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
HARD_PWM = 43


model, JETSON_INFO, _channel_data_by_mode = gpio_pin_data.get_data()
RPI_INFO = JETSON_INFO

# Dictionary objects used as lookup tables for pin to linux gpio mapping
_channel_data = {}

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


def _channel_to_info_lookup(channel, need_gpio, need_pwm):
    if channel not in _channel_data:
        raise ValueError("Channel %s is invalid" % str(channel))
    ch_info = _channel_data[channel]
    if need_gpio and ch_info.gpio_chip_dir is None:
        raise ValueError("Channel %s is not a GPIO" % str(channel))
    if need_pwm and ch_info.pwm_chip_dir is None:
        raise ValueError("Channel %s is not a PWM" % str(channel))
    return ch_info


def _channel_to_info(channel, need_gpio=False, need_pwm=False):
    _validate_mode_set()
    return _channel_to_info_lookup(channel, need_gpio, need_pwm)


def _channels_to_infos(channels, need_gpio=False, need_pwm=False):
    _validate_mode_set()
    return [_channel_to_info_lookup(c, need_gpio, need_pwm)
            for c in _make_iterable(channels)]


def _sysfs_channel_configuration(ch_info):
    """Return the current configuration of a channel as reported by sysfs. Any
    of IN, OUT, PWM, or None may be returned."""

    if ch_info.pwm_chip_dir is not None:
        pwm_dir = "%s/pwm%i" % (ch_info.pwm_chip_dir, ch_info.pwm_id)
        if os.path.exists(pwm_dir):
            return HARD_PWM

    gpio_dir = _SYSFS_ROOT + "/" + ch_info.gpio_name
    if not os.path.exists(gpio_dir):
        return None

    with open(gpio_dir + "/direction", 'r') as f_direction:
        gpio_direction = f_direction.read()

    lookup = {
        'in': IN,
        'out': OUT,
    }
    return lookup.get(gpio_direction.strip().lower(), None)


def _app_channel_configuration(ch_info):
    """Return the current configuration of a channel as requested by this
    module in this process. Any of IN, OUT, or None may be returned."""

    return _channel_configuration.get(ch_info.channel, None)


def _export_gpio(ch_info):
    if not os.path.exists(_SYSFS_ROOT + "/" + ch_info.gpio_name):
        with open(_SYSFS_ROOT + "/export", "w") as f_export:
            f_export.write(str(ch_info.gpio))

    while not os.access(_SYSFS_ROOT + "/" + ch_info.gpio_name + "/value",
                        os.R_OK | os.W_OK):
        time.sleep(0.01)

    ch_info.f_direction = open(_SYSFS_ROOT + "/" + ch_info.gpio_name + "/direction", 'w')
    ch_info.f_value = open(_SYSFS_ROOT + "/" + ch_info.gpio_name + "/value", 'r+')


def _unexport_gpio(ch_info):
    ch_info.f_direction.close()
    ch_info.f_value.close()

    if os.path.exists(_SYSFS_ROOT + "/" + ch_info.gpio_name):
        with open(_SYSFS_ROOT + "/unexport", "w") as f_unexport:
            f_unexport.write(str(ch_info.gpio))


def _output_one(ch_info, value):
    ch_info.f_value.seek(0)
    ch_info.f_value.write(str(int(bool(value))))
    ch_info.f_value.flush()


def _setup_single_out(ch_info, initial=None):
    _export_gpio(ch_info)

    ch_info.f_direction.seek(0)
    ch_info.f_direction.write("out")
    ch_info.f_direction.flush()

    if initial is not None:
        _output_one(ch_info, initial)

    _channel_configuration[ch_info.channel] = OUT


def _setup_single_in(ch_info):
    _export_gpio(ch_info)

    ch_info.f_direction.seek(0)
    ch_info.f_direction.write("in")
    ch_info.f_direction.flush()

    _channel_configuration[ch_info.channel] = IN


def _pwm_path(ch_info):
    return ch_info.pwm_chip_dir + '/pwm' + str(ch_info.pwm_id)


def _pwm_export_path(ch_info):
    return ch_info.pwm_chip_dir + '/export'


def _pwm_unexport_path(ch_info):
    return ch_info.pwm_chip_dir + '/unexport'


def _pwm_period_path(ch_info):
    return _pwm_path(ch_info) + "/period"


def _pwm_duty_cycle_path(ch_info):
    return _pwm_path(ch_info) + "/duty_cycle"


def _pwm_enable_path(ch_info):
    return _pwm_path(ch_info) + "/enable"


def _export_pwm(ch_info):
    if not os.path.exists(_pwm_path(ch_info)):
        with open(_pwm_export_path(ch_info), 'w') as f:
            f.write(str(ch_info.pwm_id))

    enable_path = _pwm_enable_path(ch_info)
    while not os.access(enable_path, os.R_OK | os.W_OK):
        time.sleep(0.01)

    ch_info.f_duty_cycle = open(_pwm_duty_cycle_path(ch_info), 'r+')

def _unexport_pwm(ch_info):
    ch_info.f_duty_cycle.close()

    with open(_pwm_unexport_path(ch_info), 'w') as f:
        f.write(str(ch_info.pwm_id))


def _set_pwm_period(ch_info, period_ns):
    with open(_pwm_period_path(ch_info), 'w') as f:
        f.write(str(period_ns))


def _set_pwm_duty_cycle(ch_info, duty_cycle_ns):
    # On boot, both period and duty cycle are both 0. In this state, the period
    # must be set first; any configuration change made while period==0 is
    # rejected. This is fine if we actually want a duty cycle of 0. Later, once
    # any period has been set, we will always be able to set a duty cycle of 0.
    # The code could be written to always read the current value, and only
    # write the value if the desired value is different. However, we enable
    # this check only for the 0 duty cycle case, to avoid having to read the
    # current value every time the duty cycle is set.
    if not duty_cycle_ns:
        ch_info.f_duty_cycle.seek(0)
        cur = ch_info.f_duty_cycle.read().strip()
        if cur == '0':
            return

    ch_info.f_duty_cycle.seek(0)
    ch_info.f_duty_cycle.write(str(duty_cycle_ns))
    ch_info.f_duty_cycle.flush()


def _enable_pwm(ch_info):
    with open(_pwm_enable_path(ch_info), 'w') as f:
        f.write("1")


def _disable_pwm(ch_info):
    with open(_pwm_enable_path(ch_info), 'w') as f:
        f.write("0")


def _cleanup_one(ch_info):
    app_cfg = _channel_configuration[ch_info.channel]
    if app_cfg == HARD_PWM:
        _disable_pwm(ch_info)
        _unexport_pwm(ch_info)
    else:
        event.event_cleanup(ch_info.gpio, ch_info.gpio_name)
        _unexport_gpio(ch_info)
    del _channel_configuration[ch_info.channel]


def _cleanup_all():
    global _gpio_mode

    for channel in list(_channel_configuration.keys()):
        ch_info = _channel_to_info(channel)
        _cleanup_one(ch_info)

    _gpio_mode = None


# Function used to enable/disable warnings during setup and cleanup.
# Param -> state is a bool
def setwarnings(state):
    global _gpio_warnings
    _gpio_warnings = bool(state)


# Function used to set the pin mumbering mode. Possible mode values are BOARD,
# BCM, TEGRA_SOC and CVM
def setmode(mode):
    global _gpio_mode, _channel_data

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

    _channel_data = _channel_data_by_mode[mode_map[mode]]
    _gpio_mode = mode


# Function used to get the currently set pin numbering mode
def getmode():
    return _gpio_mode


# Mutable class to represent a default function argument.
# See https://stackoverflow.com/a/57628817/2767322
class _Default:
    def __init__(self, val):
        self.val = val


# Function used to setup individual pins or lists/tuples of pins as
# Input or Output. Param channels must an integer or list/tuple of integers,
# direction must be IN or OUT, pull_up_down must be PUD_OFF, PUD_UP or
# PUD_DOWN and is only valid when direction in IN, initial must be HIGH or LOW
# and is only valid when direction is OUT
def setup(channels, direction, pull_up_down=_Default(PUD_OFF), initial=None):
    if pull_up_down in setup.__defaults__:
        pull_up_down_explicit = False
        pull_up_down = pull_up_down.val
    else:
        pull_up_down_explicit = True

    ch_infos = _channels_to_infos(channels, need_gpio=True)

    # check direction is valid
    if direction != OUT and direction != IN:
        raise ValueError("An invalid direction was passed to setup()")

    # check if pullup/down is used with output
    if direction == OUT and pull_up_down != PUD_OFF:
        raise ValueError("pull_up_down parameter is not valid for outputs")

    # check if pullup/down value is specified and/or valid
    if pull_up_down_explicit:
        warnings.warn("Jetson.GPIO ignores setup()'s pull_up_down parameter")
    if (pull_up_down != PUD_OFF and pull_up_down != PUD_UP and
            pull_up_down != PUD_DOWN):
        raise ValueError("Invalid value for pull_up_down; should be one of"
                         "PUD_OFF, PUD_UP or PUD_DOWN")

    if _gpio_warnings:
        for ch_info in ch_infos:
            sysfs_cfg = _sysfs_channel_configuration(ch_info)
            app_cfg = _app_channel_configuration(ch_info)

            # warn if channel has been setup external to current program
            if app_cfg is None and sysfs_cfg is not None:
                warnings.warn(
                    "This channel is already in use, continuing anyway. "
                    "Use GPIO.setwarnings(False) to disable warnings",
                    RuntimeWarning)

    if direction == OUT:
        initial = _make_iterable(initial, len(ch_infos))
        if len(initial) != len(ch_infos):
            raise RuntimeError("Number of values != number of channels")
        for ch_info, init in zip(ch_infos, initial):
            _setup_single_out(ch_info, init)
    else:
        if initial is not None:
            raise ValueError("initial parameter is not valid for inputs")
        for ch_info in ch_infos:
            _setup_single_in(ch_info)


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

    ch_infos = _channels_to_infos(channel)
    for ch_info in ch_infos:
        if ch_info.channel in _channel_configuration:
            _cleanup_one(ch_info)


# Function used to return the current value of the specified channel.
# Function returns either HIGH or LOW
def input(channel):
    ch_info = _channel_to_info(channel, need_gpio=True)

    app_cfg = _app_channel_configuration(ch_info)
    if app_cfg not in [IN, OUT]:
        raise RuntimeError("You must setup() the GPIO channel first")

    ch_info.f_value.seek(0)
    value_read = int(ch_info.f_value.read())
    return value_read


# Function used to set a value to a channel or list/tuple of channels.
# Parameter channels must be an integer or list/tuple of integers.
# Values must be either HIGH or LOW or list/tuple
# of HIGH and LOW with the same length as the channels list/tuple
def output(channels, values):
    ch_infos = _channels_to_infos(channels, need_gpio=True)
    values = _make_iterable(values, len(ch_infos))
    if len(values) != len(ch_infos):
        raise RuntimeError("Number of values != number of channels")

    # check that channels have been set as output
    if any(_app_channel_configuration(ch_info) != OUT for ch_info in ch_infos):
        raise RuntimeError("The GPIO channel has not been set up as an "
                           "OUTPUT")

    for ch_info, value in zip(ch_infos, values):
        _output_one(ch_info, value)


# Function used to check if an event occurred on the specified channel.
# Param channel must be an integer.
# This function return True or False
def event_detected(channel):
    ch_info = _channel_to_info(channel, need_gpio=True)

    if _app_channel_configuration(ch_info) != IN:
        raise RuntimeError("You must setup() the GPIO channel as an "
                           "input first")

    return event.edge_event_detected(ch_info.gpio)


# Function used to add a callback function to channel, after it has been
# registered for events using add_event_detect()
def add_event_callback(channel, callback):
    ch_info = _channel_to_info(channel, need_gpio=True)
    if not callable(callback):
        raise TypeError("Parameter must be callable")

    if _app_channel_configuration(ch_info) != IN:
        raise RuntimeError("You must setup() the GPIO channel as an "
                           "input first")

    if not event.gpio_event_added(ch_info.gpio):
        raise RuntimeError("Add event detection using add_event_detect first "
                           "before adding a callback")

    event.add_edge_callback(ch_info.gpio, lambda: callback(channel))


# Function used to add threaded event detection for a specified gpio channel.
# Param gpio must be an integer specifying the channel, edge must be RISING,
# FALLING or BOTH. A callback function to be called when the event is detected
# and an integer bounctime in milliseconds can be optionally provided
def add_event_detect(channel, edge, callback=None, bouncetime=None):
    ch_info = _channel_to_info(channel, need_gpio=True)
    if (not callable(callback)) and callback is not None:
        raise TypeError("Callback Parameter must be callable")

    # channel must be setup as input
    if _app_channel_configuration(ch_info) != IN:
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

    result = event.add_edge_detect(ch_info.gpio, ch_info.gpio_name,
                                   edge - _EDGE_OFFSET, bouncetime)

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
        event.add_edge_callback(ch_info.gpio, lambda: callback(channel))


# Function used to remove event detection for channel
def remove_event_detect(channel):
    ch_info = _channel_to_info(channel, need_gpio=True)
    event.remove_edge_detect(ch_info.gpio, ch_info.gpio_name)


# Function used to perform a blocking wait until the specified edge
# is detected for the param channel. Channel must be an integer and edge must
# be either RISING, FALLING or BOTH.
# bouncetime in milliseconds and timeout in millseconds can optionally be
# provided
def wait_for_edge(channel, edge, bouncetime=None, timeout=None):
    ch_info = _channel_to_info(channel, need_gpio=True)

    # channel must be setup as input
    if _app_channel_configuration(ch_info) != IN:
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

    result = event.blocking_wait_for_edge(ch_info.gpio, ch_info.gpio_name,
                                          edge - _EDGE_OFFSET, bouncetime,
                                          timeout)

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
    ch_info = _channel_to_info(channel)
    func = _sysfs_channel_configuration(ch_info)
    if func is None:
        func = UNKNOWN
    return func


class PWM(object):
    def __init__(self, channel, frequency_hz):
        self._ch_info = _channel_to_info(channel, need_pwm=True)

        app_cfg = _app_channel_configuration(self._ch_info)
        if app_cfg == HARD_PWM:
            raise ValueError("Can't create duplicate PWM objects")
        # Apps typically set up channels as GPIO before making them be PWM,
        # because RPi.GPIO does soft-PWM. We must undo the GPIO export to
        # allow HW PWM to run on the pin.
        if app_cfg in [IN, OUT]:
            cleanup(channel)

        if _gpio_warnings:
            sysfs_cfg = _sysfs_channel_configuration(self._ch_info)
            app_cfg = _app_channel_configuration(self._ch_info)

            # warn if channel has been setup external to current program
            if app_cfg is None and sysfs_cfg is not None:
                warnings.warn(
                    "This channel is already in use, continuing anyway. "
                    "Use GPIO.setwarnings(False) to disable warnings",
                    RuntimeWarning)

        _export_pwm(self._ch_info)
        self._started = False
        _set_pwm_duty_cycle(self._ch_info, 0)
        # Anything that doesn't match new frequency_hz
        self._frequency_hz = -1 * frequency_hz
        self._reconfigure(frequency_hz, 0.0)

        _channel_configuration[channel] = HARD_PWM

    def __del__(self):
        if _channel_configuration.get(self._ch_info.channel, None) != HARD_PWM:
            # The user probably ran cleanup() on the channel already, so avoid
            # attempts to repeat the cleanup operations.
            return
        self.stop()
        _unexport_pwm(self._ch_info)
        del _channel_configuration[self._ch_info.channel]

    def start(self, duty_cycle_percent):
        self._reconfigure(self._frequency_hz, duty_cycle_percent, start=True)

    def ChangeFrequency(self, frequency_hz):
        self._reconfigure(frequency_hz, self._duty_cycle_percent)

    def ChangeDutyCycle(self, duty_cycle_percent):
        self._reconfigure(self._frequency_hz, duty_cycle_percent)

    def stop(self):
        if not self._started:
            return
        _disable_pwm(self._ch_info)

    def _reconfigure(self, frequency_hz, duty_cycle_percent, start=False):
        if duty_cycle_percent < 0.0 or duty_cycle_percent > 100.0:
            raise ValueError("")

        freq_change = start or (frequency_hz != self._frequency_hz)
        stop = self._started and freq_change
        if stop:
            self._started = False
            _disable_pwm(self._ch_info)

        if freq_change:
            self._frequency_hz = frequency_hz
            self._period_ns = int(1000000000.0 / frequency_hz)
            _set_pwm_period(self._ch_info, self._period_ns)

        self._duty_cycle_percent = duty_cycle_percent
        self._duty_cycle_ns = int(self._period_ns *
                                  (duty_cycle_percent / 100.0))
        _set_pwm_duty_cycle(self._ch_info, self._duty_cycle_ns)

        if stop or start:
            _enable_pwm(self._ch_info)
            self._started = True
