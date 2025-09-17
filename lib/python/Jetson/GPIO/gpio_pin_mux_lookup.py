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

# @File name: gpio_pin_mux_lookup.py
# @Date:
# @Last modified by:
# @Last Modified time: 9/17/2025
# @Description: Simple tool to lookup pin mux register address for GPIO pins. User must specify the BOARD mode GPIO pin number.

import sys
import gpio_pin_data

# @brief Get pin register address for a given BOARD mode GPIO pin number.
# @param[in] gpio_pin: BOARD mode GPIO pin number
# @param[in] pin_defs: pin definitions
# @return pin register address
def lookup_mux_register(gpio_pin, pin_defs):
    # Find pin definition with matching pin number
    for pin_def in pin_defs:
        board_mode_pin_num = pin_def[3]
        if board_mode_pin_num == gpio_pin:
            #return the sum of the register block base address and the register offset
            return pin_def[9] + pin_def[10]
    
    return -1

# @brief Main function to handle command line interface.
def main():
    if len(sys.argv) != 2:
        print("Usage: jetson-gpio-pin-mux-lookup <gpio_pin_number>")
        print("\nLookup pin mux register address for GPIO pins.")
        print("Specify the Board Mode GPIO pin number (e.g., 7, 11, 40, etc.)")
        print("\nExample:")
        print("  jetson-gpio-pin-mux-lookup 7")
        sys.exit(1)
    
    try:
        gpio_pin = int(sys.argv[1])
    except ValueError:
        print(f"Error: GPIO pin number must be an integer, got '{sys.argv[1]}'", file=sys.stderr)
        sys.exit(1)

    model = gpio_pin_data.get_model()
    pin_defs = gpio_pin_data.jetson_gpio_data[model][0]
    
    # Validate GPIO pin range
    if gpio_pin < 0 or gpio_pin > 40:
        print(f"Error: GPIO pin number {gpio_pin} is out of valid range (0-40)", file=sys.stderr)
        sys.exit(1)
    
    # Get pin register address
    pin_register_address = lookup_mux_register(gpio_pin, pin_defs)
    
    if pin_register_address == -1:
        print(f"Error: GPIO pin {gpio_pin} not found in {model} pin definitions", file=sys.stderr)
        sys.exit(1)


    print(f"GPIO Pin {gpio_pin}: Mux Register Address = 0x{pin_register_address:X}")

if __name__ == '__main__':
    main()
