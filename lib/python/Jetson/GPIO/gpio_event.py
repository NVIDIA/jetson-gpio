# Copyright (c) 2012-2017 Ben Croston <ben@croston.org>.
# Copyright (c) 2019-2023, NVIDIA CORPORATION. All rights reserved.
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

# @File name: gpio_event.py
# @Date:
# @Last modified by:
# @Last Modified time: 6/20/2023
# @Description: This file manages all function needed for event detection
# that enables users to add or remove an event in a blocking or non-blocking
# mode. It keeps an global event dictionary that supports looking up a
# channel's registered event.
# @Note: Ideas for multiple channel detection
#   1. polling for maxevents should not be specified
#   2. Each thread should not share epoll instance

# Python2 has module thread. Renamed to _thread in Python3
try:
    import thread
except:
    import _thread as thread

import os
import warnings
import fcntl
import select
import ctypes
import time

from Jetson.GPIO import gpio_cdev as cdev
from datetime import datetime

try:
    InterruptedError = InterruptedError
except:
    InterruptedError = IOError


# Edge possibilities
NO_EDGE = 0
RISING_EDGE = 1
FALLING_EDGE = 2
BOTH_EDGE = 3

# Dictionary storing the epoll thread object
# Key: channel (pin number), Value: Epoll object
_epoll_fd_thread = {}

# epoll blocking wait object
_epoll_fd_blocking = None

# 2-layered dictionary of GPIO class objects.
# layer 1 key = chip name, layer 2 key = channel (pin number by mode)
# value = GPIO class object
_gpio_event_list = {}

# Dictionary for thread to lookup to check its supposed state
# Key: thread id, Value: true if it is supposed to be running state, otherwise false
_thread_running_dict = {}

# lock object for thread
_mutex = thread.allocate_lock()

class _Gpios:
    # @value_fd the file descriptor for the chip line
    # @initial_thread true if the thread just start up (within the first loop)
    # @thread_added the number of threads being added to monitor this object/gpio
    # @thread_id the id of the thread being created to detect event
    # @bouncetime the time interval for debouncing
    # @callbacks a list of callback functions to be executed when an edge event happened
    # @lastcall the timestamp for counting debounce
    # @event_occurred true if an edge event occured
    def __init__(self, line_fd, bouncetime=None):
        self.value_fd = line_fd
        self.initial_thread = True
        self.thread_added = False
        self.thread_id = 0
        self.thread_exited = False
        self.bouncetime = bouncetime
        self.callbacks = []
        self.lastcall = 0
        self.event_occurred = False

    def __del__(self):
        del self.callbacks

# @brief adding an edge detecting event
#   The detection event runs in an thread that enables non-blocking I/O multiplexing approach.
#   However, one pin on a chip (channel) can only allow one edge detection event, the new added
#   event will be removed if there's an existing event.
# @param[in] chip_fd: file descriptor
# @param[in] chip_name: the GPIO chip name/instance
# @param[in] channel: the file descriptor for the chip line
# @param[in] request: gpioevent_request struct that describes gpio event monitoring
# @param[in] bouncetime: the time interval for debouncing
# @param[in] poll_time: the max time to wait for an edge event
# @param[out] success on 0, otherwise return 2 if something fatal happened
def add_edge_detect(chip_fd, chip_name, channel, request, bouncetime, poll_time):
    gpio_obj = None
    res = gpio_event_added(chip_name, channel)

    # event not added
    if not res:
        # open the line
        try:
            ioctl_ret = fcntl.ioctl(chip_fd, cdev.GPIO_GET_LINEEVENT_IOCTL, request)
        except (OSError, IOError) as e:
            raise cdev.GPIOError(e.errno, "Opening input line event handle: " + e.strerror)
    else:
        warnings.warn("Warning: event is already added, ignore new added event", RuntimeWarning)
        return 1

    # Check if we successfully get the event handle from ioctl
    if ioctl_ret < 0:
        raise cdev.GPIOError("Unable to get line event handle", e.strerror)
    else:
        gpio_obj = _Gpios(request.fd, bouncetime)

    # create epoll object for fd if not already open
    _mutex.acquire()
    if channel not in _epoll_fd_thread:
        _epoll_fd_thread[channel] = select.epoll()
        if _epoll_fd_thread[channel] is None:
            _mutex.release()

            return 2

    # add eventmask and fd to epoll object
    try:
        # eventmask: available for read and edge trigger
        _epoll_fd_thread[channel].register(gpio_obj.value_fd, select.EPOLLIN | select.EPOLLET)
    except IOError:
        _mutex.release()
        remove_edge_detect(chip_name, channel)

        return 2
    _mutex.release()

    # create and start poll thread if not already running
    try:
        thread_id = thread.start_new_thread(_edge_handler, ("edge_handler_thread", request.fd, channel, poll_time))
        gpio_obj.thread_id = thread_id
    except:
        remove_edge_detect(chip_name, channel)
        warnings.warn("Unable to start thread", RuntimeWarning)

        return 2

    gpio_obj.thread_added = True
    _add_gpio_event(chip_name, channel, gpio_obj)

    return 0

# @brief Remove an edge event detection
#   Not only will the event be unregistered, the thread corresponds will also be cleared.
# Suggestion about the timeout parameter: the value should be greater than the poll_time
# in add_edge_detect to keep it safe. This event returns without doing anything if the
# event corresponding to the chip_name and channel is not found.
# @param[in] chip_name: the GPIO chip name/instance
# @param[in] channel: the pin number in specified mode (board or bcm)
# @param[in] timeout: the maximum time to wait for the thread detecting channel to stop
def remove_edge_detect(chip_name, channel, timeout=0.3):
    gpio_obj = gpio_event_added(chip_name, channel)

    if gpio_obj is None:
        return

    # Have the thread to be in an exit state
    _mutex.acquire()
    thread_id = _gpio_event_list[chip_name][channel].thread_id
    _thread_running_dict[thread_id] = False

    # Wait till the thread exits
    if _gpio_event_list[chip_name][channel].thread_added == True:
        _mutex.release()
        time.sleep(timeout)
        _mutex.acquire()

        if _gpio_event_list[chip_name][channel].thread_exited == False:
            warnings.warn("Timeout in waiting event detection to be removed", RuntimeWarning)

    # unregister the epoll file descriptor
    if channel in _epoll_fd_thread and _epoll_fd_thread[channel] is not None:
        _epoll_fd_thread[channel].unregister(_gpio_event_list[chip_name][channel].value_fd)

    del _gpio_event_list[chip_name][channel]
    _mutex.release()

# @brief Add a callback function for an event
#   Note that if the function does not exist or the event has not been set up, warning
#   will be shown, ignoring the action
# @param[in] chip_name: the GPIO chip name/instance
# @param[in] channel: the pin number in specified mode (board or bcm)
# @param[in] callback: a callback function
def add_edge_callback(chip_name, channel, callback):
    gpio_obj = gpio_event_added(chip_name, channel)

    if gpio_obj is None:
        warnings.warn("Event not found", RuntimeWarning)
        return

    _mutex.acquire()
    if not _gpio_event_list[chip_name][channel].thread_added:
        _mutex.release()
        warnings.warn("Please add the event before adding callback", RuntimeWarning)
        return

    _gpio_event_list[chip_name][channel].callbacks.append(callback)
    _mutex.release()

# @brief Check if any edge event occured
#   If an adge event happened, the flag will be cleared for the next occurance
# @param[in] chip_name: the GPIO chip name/instance
# @param[in] channel: the pin number in specified mode (board or bcm)
# @param[out] true if an edge event occured, otherwise false
def edge_event_detected(chip_name, channel):
    gpio_obj = gpio_event_added(chip_name, channel)

    if gpio_obj is None:
        warnings.warn("Event not found", RuntimeWarning)
        return False

    _mutex.acquire()
    # Event has occured
    if _gpio_event_list[chip_name][channel].event_occurred:
        _gpio_event_list[chip_name][channel].event_occurred = False
        _mutex.release()

        return True
    _mutex.release()

    return False

# @brief Check if any event is added to the channel in the chip controller
# @param[in] chip_name: the GPIO chip name/instance
# @param[in] channel: the pin number in specified mode (board or bcm)
# @param[out] the gpio object if an event exists, otherwise None
def gpio_event_added(chip_name, channel):
    _mutex.acquire()
    if chip_name not in _gpio_event_list:
        _mutex.release()
        return None
    if channel not in _gpio_event_list[chip_name]:
        _mutex.release()
        return None

    gpio_obj = _gpio_event_list[chip_name][channel]
    _mutex.release()

    return gpio_obj

# @brief Add an event to the event list
# @param[in] chip_name: the GPIO chip name/instance
# @param[in] channel: the pin number in specified mode (board or bcm)
# @param[in] gpio_obj: the gpio handle with related information of a channel's
# event
def _add_gpio_event(chip_name, channel, gpio_obj):
    _mutex.acquire()
    if chip_name not in _gpio_event_list:
        _gpio_event_list[chip_name] = {}

    if channel not in _gpio_event_list[chip_name]:
        _gpio_event_list[chip_name][channel] = gpio_obj
    _mutex.release()

# @brief Look up by chip name and channel to get the gpio object
#   with related information of a channel's event
# @param[in] chip_name: the GPIO chip name/instance
# @param[in] channel: the pin number in specified mode (board or bcm)
# @param[out] the gpio handle with related information of a channel's event,
# if such handle exist, otherwise return None
def _get_gpio_object(chip_name, channel):
    gpio_obj = gpio_event_added(chip_name, channel)

    if gpio_obj is None:
        warnings.warn("Event not found", RuntimeWarning)
        return None

    _mutex.acquire()
    gpio_obj = _gpio_event_list[chip_name][channel]
    _mutex.release()

    return gpio_obj


def _set_edge(gpio_name, edge):
    raise RuntimeError("This function is deprecated")

# @brief Look up by chip name and channel to get the gpio object
#   with related information of a channel's event
# @param[in] fd: the file descriptor of a channel/line
# @param[out] a tuple of the GPIO chip name and the pin number in
# specified mode, otherwise return a tuple of None
def _get_gpio_obj_keys(fd):
    _mutex.acquire()
    for chip_name in _gpio_event_list:
        for pin in _gpio_event_list[chip_name]:
            if _gpio_event_list[chip_name][pin].value_fd == fd:
                _mutex.release()

                return (chip_name, pin)

    _mutex.release()
    return None, None

def _get_gpio_file_object(fileno):
    raise RuntimeError("This function is deprecated")


def _set_thread_exit_state(fd):
    chip_name, channel = _get_gpio_obj_keys(fd)

    # Get the gpio object to do following updates
    gpio_obj = _get_gpio_object(chip_name, channel)
    if gpio_obj == None:
        warnings.warn("Channel has been remove from detection before thread exits", RuntimeWarning)
        return

    # Set state
    _mutex.acquire()
    _gpio_event_list[chip_name][channel].thread_exited = True
    _mutex.release()


# @brief A thread that catches GPIO events in a non-blocking mode.
#   Exit upon error (may be fd non-existance, information descrepency,
#   unknown error)
# @param[in] thread_name: a functional name of the thread
# @param[in] fd: the file descriptor of a channel/line
# @param[in] channel: the pin number in specified mode (board or bcm)
# @param[in] poll_timeout: the maximum time set to wait for edge event (second)
def _edge_handler(thread_name, fileno, channel, poll_timeout):
    thread_id = thread.get_ident()

    # Mark the thread state as running
    _mutex.acquire()
    _thread_running_dict[thread_id] = True

    # clean device buffer
    epoll_obj = _epoll_fd_thread[channel]
    _mutex.release()

     # The timeout should be longer than the wait time between the events
    precedent_events = epoll_obj.poll(timeout=0.5, maxevents=1)
    if len(precedent_events) > 0:
        _fd = precedent_events[0][0]

        try:
            data = os.read(_fd, ctypes.sizeof(cdev.gpioevent_data))
        except OSError as e:
            raise cdev.GPIOError(e.errno, "Reading GPIO event: " + e.strerror)

    while _thread_running_dict[thread_id]:
        try:
            # poll for event
            events = epoll_obj.poll(timeout=poll_timeout, maxevents=1)

            # Timeout without any event
            if len(events) == 0:
                # The timeout is especially added to confirm the thread running status, so
                # it is a design that no warning signal is shown when timeout
                continue
            fd = events[0][0]

            # Check if the returning fd is the one we are waiting for
            if fd != fileno:
                raise RuntimeError("File object not found after wait for GPIO %s" % channel)

            #read the result out
            try:
                data = os.read(fd, ctypes.sizeof(cdev.gpioevent_data))
            except OSError as e:
                raise cdev.GPIOError(e.errno, "Reading GPIO event: " + e.strerror)

            event_data = cdev.gpioevent_data.from_buffer_copy(data)

            # event result
            if (event_data.id != cdev.GPIOEVENT_REQUEST_RISING_EDGE and
                event_data.id != cdev.GPIOEVENT_REQUEST_FALLING_EDGE):
                warnings.warn("Unknown event caught", RuntimeWarning)
                continue

            # check key to make sure gpio object has not been deleted
            # from main thread
            chip_name, pin_num = _get_gpio_obj_keys(fd)
            if channel != pin_num:
                warnings.warn("Channel does not match with assigned file descriptor", RuntimeWarning)

                _mutex.acquire()
                _thread_running_dict[thread.get_ident()] = False
                _mutex.release()
                break

            # Get the gpio object to do following updates
            gpio_obj = _get_gpio_object(chip_name, pin_num)
            if gpio_obj is None:
                raise RuntimeError("GPIO object does not exists")

            # debounce the input event for the specified bouncetime
            time = datetime.now()
            time = time.second * 1E6 + time.microsecond
            if (gpio_obj.bouncetime is None or
                    (time - gpio_obj.lastcall >
                        gpio_obj.bouncetime * 1000) or
                    (gpio_obj.lastcall == 0) or gpio_obj.lastcall > time):
                gpio_obj.lastcall = time
                gpio_obj.event_occurred = True

                #update to the original list
                _mutex.acquire()
                _gpio_event_list[chip_name][pin_num] = gpio_obj
                _mutex.release()

                # callback function
                for cb_func in gpio_obj.callbacks:
                    cb_func()

        # if interrupted by a signal, continue to start of the loop
        except InterruptedError:
            continue
        except AttributeError:
            break
        finally:
            if _mutex.locked():
                _mutex.release()

    _set_thread_exit_state(fileno)
    thread.exit()

# This function waits for a edge event in a blocking mode, which the user must
# specify the file descriptor of the chip, which channel of the chip, the event handle,
# time for debouncing in milliseconds, the time limit to wait for the event.
# return value: -2 for fatal errors, -1 if edge is already being detected, 0 if timeout
# occured, and 1 if event was valid
def blocking_wait_for_edge(chip_fd, chip_name, channel, request, bouncetime, timeout):
    # check if gpio edge already added. Add if not already added
    gpio_obj = gpio_event_added(chip_name, channel)
    if gpio_obj != None:
        return -1
    else:
        try:
            fcntl.ioctl(chip_fd, cdev.GPIO_GET_LINEEVENT_IOCTL, request)
        except (OSError, IOError) as e:
            raise cdev.GPIOError(e.errno, "Opening input line event handle: " + e.strerror)
        gpio_obj = _Gpios(request.fd, bouncetime)
        # As object is added to gpio event list here, we need to return it when
        # the function return
        _add_gpio_event(chip_name, channel, gpio_obj)

    ret = select.select([request.fd], [], [], timeout)

    if ret[0] == [request.fd]:
        try:
            data = os.read(request.fd, ctypes.sizeof(cdev.gpioevent_data))
        except OSError as e:
            remove_edge_detect(chip_name, channel)
            raise cdev.GPIOError(e.errno, "Reading GPIO event: " + e.strerror)

        event_data = cdev.gpioevent_data.from_buffer_copy(data)

        if (event_data.id != cdev.GPIOEVENT_REQUEST_RISING_EDGE and
            event_data.id != cdev.GPIOEVENT_REQUEST_FALLING_EDGE):
            warnings.warn("Unknown event caught", RuntimeWarning)
            remove_edge_detect(chip_name, channel)
            return -2
        remove_edge_detect(chip_name, channel)
        return int(ret != [])
    elif len(ret[0]) == 0:
        # Timeout
        remove_edge_detect(chip_name, channel)
        return 0
    remove_edge_detect(chip_name, channel)
    return -2


# @brief clean up the event registered on the name of chip and channel
#   Note that the event detection thread will also be removed
# @param[in] chip_name: the GPIO chip name/instance
# @param[in] channel: the pin number in specified mode (board or bcm)
def event_cleanup(chip_name, channel):
    global _epoll_fd_blocking

    #remove all the event being detected in the event list
    remove_edge_detect(chip_name, channel)

    #unregister the device being polled
    _mutex.acquire()
    for gpio_chip in _gpio_event_list.copy():
        # Warning: this is only for single threaded solution
        if channel not in _gpio_event_list[gpio_chip]:
            # It is a design decision that every pin owns its epoll object
            if _epoll_fd_blocking is not None:
                _epoll_fd_blocking.close()
                _epoll_fd_blocking = None

            if channel in _epoll_fd_thread and _epoll_fd_thread[channel] is not None:
                _epoll_fd_thread[channel].close()
                del _epoll_fd_thread[channel]

    _mutex.release()
