#!/bin/bash

# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
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

script_dir="$(dirname "$0")"
script_dir="$(cd "${script_dir}" && pwd)"
top_dir="$(dirname "${script_dir}")"
py_lib_dir="$(cd "${top_dir}/lib/python" && pwd)"

# prints usage
print_help() {
    cat << EOF
Usage: run_sample.sh <sample application>
sample_application: simple_input.py
                    simple_output.py
                    simple_pwm.py
                    button_led.py
                    button_event.py
                    button_interrupt.py
                    test_all_apis.py
                    test_all_pins.py
EOF
    exit 1
}

# Check if the necessary argument is provided
if [ "$#" -lt "1" ]; then
    print_help
fi

# Check if --help or -h switch is the argument
arg="$1"
if [ "${arg}" = "--help" ] || [ "${arg}" = "-h" ]; then
    print_help
fi

# Set PYTHONPATH to locate the required python modules
export PYTHONPATH="${py_lib_dir}${PYTHONPATH+:}${PYTHONPATH}"

# Run the requested sample application
exec "${script_dir}/${arg}" "${@:2}"
