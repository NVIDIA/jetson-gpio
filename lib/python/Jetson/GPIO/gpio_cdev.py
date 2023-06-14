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

# @File name: gpio_cdev.py
# @Date:  
# @Last modified by:  
# @Last Modified time: 6/6/2023
# @Description: This file provides the interface to the GPIO controller 
# in form of a character device. File operations such as open, close, 
#  ioctl, etc are provided for usage to interact with the GPIO controller.

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

# @brief the information about a GPIO chip
# @name: the Linux kernel name of the chip
# @label: a name for the chip
# @lines: number of GPIO lines on this chip
class gpiochip_info(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char * 32),
        ('label', ctypes.c_char * 32),
        ('lines', ctypes.c_uint32),
    ]

# @brief the information about a GPIO handle request
# @lineoffsets: an array of lines, specified by offset index
# @flags: flags for the GPIO lines (the flag applies to all)
# @default_values: the default output value, expecting 0 or 1
#  anything else will be interpreted as 1 
# @consumer_label: a label for the selected GPIO line(s)
# @lines: number of lines requested in this request
# @fd: this field will contain a valid file handle (value that 
# is equal or smaller than 0 means error) on success
class gpiohandle_request(ctypes.Structure):
    _fields_ = [
        ('lineoffsets', ctypes.c_uint32 * 64),
        ('flags', ctypes.c_uint32),
        ('default_values', ctypes.c_uint8 * 64),
        ('consumer_label', ctypes.c_char * 32),
        ('lines', ctypes.c_uint32),
        ('fd', ctypes.c_int),
    ]

# @brief the information of values on a GPIO handle
# @values: current state of a line (get), contain the desired 
# target state (set)
class gpiohandle_data(ctypes.Structure):
    _fields_ = [
        ('values', ctypes.c_uint8 * 64),
    ]

# @brief the information about a GPIO line
# @line_offset: the local offset on this GPIO device
# @flags: flags for this line
# @name: the name of this GPIO line
# @consumer: a functional name for the consumer of this GPIO line as set by
# whatever is using it
class gpioline_info(ctypes.Structure):
     _fields_ = [
        ('line_offset', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('name', ctypes.c_char * 32),
        ('consumer', ctypes.c_char * 32),
    ]

# @brief the information about a change in a GPIO line's status
# @timestamp: estimated time of status change occurrence (ns)
# @event_type: type of event
# @info: updated line info
class gpioline_info_changed(ctypes.Structure):
    _fields_ = [
        ('line_info', gpioline_info),
        ('timestamp', ctypes.c_uint64),
        ('event_type', ctypes.c_uint32),
        ('padding', ctypes.c_uint32 * 5),
    ]

# @brief the information about a GPIO event request
# @lineoffset: the line to subscribe to events from in offset index 
# @handleflags: handle flags for the GPIO line
# @eventflags: desired flags for the GPIO event line (what edge)
# @consumer_label: a consumer label for the selected GPIO line(s)
# @fd: contain a valid file handle if successful, otherwise zero or 
# negative value
class gpioevent_request(ctypes.Structure):
    _fields_ = [
        ('lineoffset', ctypes.c_uint32),
        ('handleflags', ctypes.c_uint32),
        ('eventflags', ctypes.c_uint32),
        ('consumer_label', ctypes.c_char * 32),
        ('fd', ctypes.c_int),
    ]

# @brief the actual event being pushed to userspace
# @timestamp: best estimate of event occurrence's time (ns)
# @id: event identifier
class gpioevent_data(ctypes.Structure):
    _fields_ = [
        ('timestamp', ctypes.c_uint64),
        ('id', ctypes.c_uint32),
    ]


class GPIOError(IOError):
    """Base class for GPIO errors."""
    pass

# @brief open a chip by its name
# @param[in] gpio_chip: name of the chip
# @param[out] the file descriptor of the chip
def chip_open(gpio_chip):
    try:
        chip_fd = os.open(gpio_chip, os.O_RDONLY)
    except OSError as e:
        raise GPIOError(e.errno, "Opening GPIO chip: " + e.strerror)

    return chip_fd

# @brief open and check the information of the chip 
# @param[in] label: label of the chip
# @param[in] gpio_chip: name of the chip
# @param[out] the file descriptor of the chip
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

# @brief open a chip by its label
# @param[in] label: 
# @param[out] the file descriptor of the chip
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

# @brief close a chip
# @param[in] chip_fd: the file descriptor of the chip
def close_chip(chip_fd):
    if chip_fd is None:
        return

    try:
        os.close(chip_fd)
    except (OSError, IOError) as e:
        pass

# @brief open a line of a chip
# @param[in] ch_info: ChannelInfo object of the channel desired to open
# @param[out] the file descriptor of the line
def open_line(ch_info, request):
    
    try:
        fcntl.ioctl(ch_info.chip_fd, GPIO_GET_LINEHANDLE_IOCTL, request)
        
    except (OSError, IOError) as e:
        raise GPIOError(e.errno, "Opening output line handle: " + e.strerror)

    ch_info.line_handle = request.fd

# @brief close a line
# @param[in] line_handle: the file descriptor of the line
def close_line(line_handle):
    if line_handle is None:
        return

    try:
        os.close(line_handle)
    except OSError as e:
        raise GPIOError(e.errno, "Closing existing GPIO line: " + e.strerror)

# @brief build a request handle struct
# @param[in] line_offset: the offset of the line to its chip
# @param[in] direction: the direction of the line (in or out)
# @param[in] initial: initial value of the line
# @param[in] consumer: the consumer label that uses the line
# @param[out] the request handle struct
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

# @brief build a request event struct
# @param[in] line_offset: the offset of the line to its chip
# @param[in] edge: event's detection edge 
# @param[in] consumer: the consumer label that uses the line
def request_event(line_offset, edge, consumer):
    request = gpioevent_request()
    request.lineoffset = line_offset
    request.handleflags = GPIOHANDLE_REQUEST_INPUT
    request.eventflags = edge
    request.consumer_label = consumer.encode()
    return request

# @brief read the value of a line
# @param[in] line_handle: file descriptor of the line
# @param[out] the value of the line
def get_value(line_handle):
    data = gpiohandle_data()

    try:
        fcntl.ioctl(line_handle, GPIOHANDLE_GET_LINE_VALUES_IOCTL, data)
    except (OSError, IOError) as e:
        raise GPIOError(e.errno, "Getting line value: " + e.strerror)

    return data.values[0]

# @brief write the value of a line
# @param[in] line_handle: file descriptor of the line
# @param[in] value: the value to set the line
def set_value(line_handle, value):
    data = gpiohandle_data()
    data.values[0] = value

    try:
        fcntl.ioctl(line_handle, GPIOHANDLE_SET_LINE_VALUES_IOCTL, data)
    except (OSError, IOError) as e:
        raise GPIOError(e.errno, "Setting line value: " + e.strerror)


