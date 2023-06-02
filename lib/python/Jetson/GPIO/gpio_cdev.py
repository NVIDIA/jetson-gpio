# Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
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

import os
import fcntl
import ctypes

GPIO_HIGH = 1

GPIOHANDLE_REQUEST_INPUT = 0x1
GPIOHANDLE_REQUEST_OUTPUT = 0x2

GPIOEVENT_REQUEST_RISING_EDGE = 0x1
GPIOEVENT_REQUEST_FALLING_EDGE = 0x2
GPIOEVENT_REQUEST_BOTH_EDGES = 0x3

GPIO_GET_CHIPINFO_IOCTL = 0x8044B401
GPIO_GET_LINEINFO_IOCTL = 0xC048B402
GPIO_GET_LINEHANDLE_IOCTL = 0xC16CB403
GPIOHANDLE_GET_LINE_VALUES_IOCTL = 0xC040B408
GPIOHANDLE_SET_LINE_VALUES_IOCTL = 0xC040B409
GPIO_GET_LINEEVENT_IOCTL = 0xC030B404

# /**
#  * struct gpiochip_info - Information about a certain GPIO chip
#  * @name: the Linux kernel name of this GPIO chip
#  * @label: a functional name for this GPIO chip, such as a product
#  * number, may be empty (i.e. label[0] == '\0')
#  * @lines: number of GPIO lines on this chip
#  */
class gpiochip_info(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char * 32),
        ('label', ctypes.c_char * 32),
        ('lines', ctypes.c_uint32),
    ]

# /**
#  * struct gpiohandle_request - Information about a GPIO handle request
#  * @lineoffsets: an array of desired lines, specified by offset index for the
#  * associated GPIO device
#  * @flags: desired flags for the desired GPIO lines, such as
#  * %GPIOHANDLE_REQUEST_OUTPUT, %GPIOHANDLE_REQUEST_ACTIVE_LOW etc, added
#  * together. Note that even if multiple lines are requested, the same flags
#  * must be applicable to all of them, if you want lines with individual
#  * flags set, request them one by one. It is possible to select
#  * a batch of input or output lines, but they must all have the same
#  * characteristics, i.e. all inputs or all outputs, all active low etc
#  * @default_values: if the %GPIOHANDLE_REQUEST_OUTPUT is set for a requested
#  * line, this specifies the default output value, should be 0 (low) or
#  * 1 (high), anything else than 0 or 1 will be interpreted as 1 (high)
#  * @consumer_label: a desired consumer label for the selected GPIO line(s)
#  * such as "my-bitbanged-relay"
#  * @lines: number of lines requested in this request, i.e. the number of
#  * valid fields in the above arrays, set to 1 to request a single line
#  * @fd: if successful this field will contain a valid anonymous file handle
#  * after a %GPIO_GET_LINEHANDLE_IOCTL operation, zero or negative value
#  * means error
#  *
#  * Note: This struct is part of ABI v1 and is deprecated.
#  * Use &struct gpio_v2_line_request instead.
#  */
class gpiohandle_request(ctypes.Structure):
    _fields_ = [
        ('lineoffsets', ctypes.c_uint32 * 64),
        ('flags', ctypes.c_uint32),
        ('default_values', ctypes.c_uint8 * 64),
        ('consumer_label', ctypes.c_char * 32),
        ('lines', ctypes.c_uint32),
        ('fd', ctypes.c_int),
    ]

# /**
#  * struct gpiohandle_data - Information of values on a GPIO handle
#  * @values: when getting the state of lines this contains the current
#  * state of a line, when setting the state of lines these should contain
#  * the desired target state
#  *
#  * Note: This struct is part of ABI v1 and is deprecated.
#  * Use &struct gpio_v2_line_values instead.
#  */
class gpiohandle_data(ctypes.Structure):
    _fields_ = [
        ('values', ctypes.c_uint8 * 64),
    ]

# /**
#  * struct gpioline_info - Information about a certain GPIO line
#  * @line_offset: the local offset on this GPIO device, fill this in when
#  * requesting the line information from the kernel
#  * @flags: various flags for this line
#  * @name: the name of this GPIO line, such as the output pin of the line on the
#  * chip, a rail or a pin header name on a board, as specified by the gpio
#  * chip, may be empty (i.e. name[0] == '\0')
#  * @consumer: a functional name for the consumer of this GPIO line as set by
#  * whatever is using it, will be empty if there is no current user but may
#  * also be empty if the consumer doesn't set this up
#  *
#  * Note: This struct is part of ABI v1 and is deprecated.
#  * Use &struct gpio_v2_line_info instead.
#  */
class gpioline_info(ctypes.Structure):
     _fields_ = [
        ('line_offset', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('name', ctypes.c_char * 32),
        ('consumer', ctypes.c_char * 32),
    ]


class gpioline_info_changed(ctypes.Structure):
    _fields_ = [
        ('line_info', gpioline_info),
        ('timestamp', ctypes.c_uint64),
        ('event_type', ctypes.c_uint32),
        ('padding', ctypes.c_uint32 * 5),
    ]


class gpioevent_request(ctypes.Structure):
    _fields_ = [
        ('lineoffset', ctypes.c_uint32),
        ('handleflags', ctypes.c_uint32),
        ('eventflags', ctypes.c_uint32),
        ('consumer_label', ctypes.c_char * 32),
        ('fd', ctypes.c_int),
    ]


class gpioevent_data(ctypes.Structure):
    _fields_ = [
        ('lineoffset', ctypes.c_uint64),
        ('id', ctypes.c_uint32),
    ]


class GPIOError(IOError):
    """Base class for GPIO errors."""
    pass


def chip_open(gpio_chip):
    try:
        chip_fd = os.open(gpio_chip, os.O_RDONLY)
    except OSError as e:
        raise GPIOError(e.errno, "Opening GPIO chip: " + e.strerror)

    return chip_fd


def chip_check_info(label, gpio_device):
    chip_fd = chip_open(gpio_device)

    chip_info = gpiochip_info()
    try:
        fcntl.ioctl(chip_fd, GPIO_GET_CHIPINFO_IOCTL, chip_info)
    except (OSError, IOError) as e:
        raise GPIOError(e.errno, "Querying GPIO chip info: " + e.strerror)

    if label != chip_info.label.decode():
        try:
            close_chip(chip_fd)
        except OSError as e:
            raise GPIOError(e.errno, "Opening GPIO chip: " + e.strerror)

        chip_fd = None

    return chip_fd


def chip_open_by_label(label):
    dev = '/dev/'
    for device in os.listdir(dev):
        if device.startswith('gpiochip'):
            gpio_device = dev + device
            chip_fd = chip_check_info(label, gpio_device)
            if chip_fd != None:
                break

    if chip_fd == None:
        raise Exception("{}: No such gpio device registered".format(label))

    return chip_fd


def close_chip(chip_fd):
    if chip_fd is None:
        return

    try:
        os.close(chip_fd)
    except (OSError, IOError) as e:
        pass


def open_line(ch_info, request):
    
    try:
        fcntl.ioctl(ch_info.chip_fd, GPIO_GET_LINEHANDLE_IOCTL, request)
        
    except (OSError, IOError) as e:
        raise GPIOError(e.errno, "Opening output line handle: " + e.strerror)

    ch_info.line_handle = request.fd


def close_line(line_handle):
    if line_handle is None:
        return

    try:
        os.close(line_handle)
    except OSError as e:
        raise GPIOError(e.errno, "Closing existing GPIO line: " + e.strerror)


def request_handle(line_offset, direction, initial, consumer):
    request = gpiohandle_request()
    request.lineoffsets[0] = line_offset
    request.flags = direction
    if direction == GPIOHANDLE_REQUEST_OUTPUT:
        request.default_values[0] = initial if initial is not None else GPIO_HIGH
    else:
        if initial is not None:
            raise ValueError("initial parameter is not valid for inputs")
    request.consumer_label = consumer.encode()
    request.lines = 1

    return request


def request_event(line_offset, edge, consumer):
    request = gpioevent_request()
    request.lineoffset = line_offset
    request.handleflags = GPIOHANDLE_REQUEST_INPUT
    request.eventflags = edge
    request.consumer_label = consumer.encode()
    return request


def get_value(line_handle):
    data = gpiohandle_data()

    try:
        fcntl.ioctl(line_handle, GPIOHANDLE_GET_LINE_VALUES_IOCTL, data)
    except (OSError, IOError) as e:
        raise GPIOError(e.errno, "Getting line value: " + e.strerror)

    return data.values[0]


def set_value(line_handle, value):
    data = gpiohandle_data()
    data.values[0] = value

    try:
        fcntl.ioctl(line_handle, GPIOHANDLE_SET_LINE_VALUES_IOCTL, data)
    except (OSError, IOError) as e:
        raise GPIOError(e.errno, "Setting line value: " + e.strerror)


