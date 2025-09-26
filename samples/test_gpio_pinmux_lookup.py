#!/usr/bin/env python

# Copyright (c) 2025, NVIDIA CORPORATION. All rights reserved.
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
import os
import sys
import subprocess

# Test data for different Jetson models
test_data = {
    'JETSON_ORIN': {
        'expected_addresses': {
            7: 0x2430070,
            11: 0x2430098,
            12: 0x2434088,
            13: 0x2430080,
            15: 0x2440020,
            16: 0xC303048,
            18: 0x2434040,
            19: 0x243D040,
            21: 0x243D018,
            22: 0x2430020,
            23: 0x243D028,
            24: 0x243D008,
            26: 0x243D038,
            29: 0xC303018,
            31: 0xC303010,
            32: 0xC303040,
            33: 0xC303000,
            35: 0x24340A0,
            36: 0x2430090,
            37: 0xC303008,
            38: 0x2434098,
            40: 0x2434090,
        }
    },
    'JETSON_ORIN_NX': {
        'expected_addresses': {
            7: 0x2448030,
            11: 0x2430098,
            12: 0x2434088,
            13: 0x243D030,
            15: 0x2440020,
            16: 0x243D020,
            18: 0x243D010,
            19: 0x243D040,
            21: 0x243D018,
            22: 0x243D000,
            23: 0x243D028,
            24: 0x243D008,
            26: 0x243D038,
            29: 0x2430068,
            31: 0x2430070,
            32: 0x2434080,
            33: 0x2434040,
            35: 0x24340A0,
            36: 0x2430090,
            37: 0x243D048,
            38: 0x2434098,
            40: 0x2434090,
        }
    }
}

tests = []

def test(f):
    tests.append(f)
    return f

# command to run the script
script_command = 'jetson-gpio-pinmux-lookup'

def run_gpio_tool(args, env=None):
    cmd = [script_command] + args
    current_env = os.environ.copy()
    if env:
        current_env.update(env)
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            env=current_env
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

# Tests for command line argument validation
@test
def test_no_arguments():
    returncode, stdout, stderr = run_gpio_tool([])
    assert returncode == 1
    assert "Usage:" in stdout
    assert "jetson-gpio-pinmux-lookup <gpio_pin_number>" in stdout
    print("✓ No arguments test passed")

@test
def test_too_many_arguments():
    returncode, stdout, stderr = run_gpio_tool(['7', '11'])
    assert returncode == 1
    assert "Usage:" in stdout
    print("✓ Too many arguments test passed")

@test
def test_non_integer_argument():
    returncode, stdout, stderr = run_gpio_tool(['abc'])
    assert returncode == 1
    assert "Error: GPIO pin number must be an integer" in stderr
    print("✓ Non-integer argument test passed")

@test
def test_negative_pin():
    test_env = {'JETSON_TESTING_MODEL_NAME': 'JETSON_ORIN'}
    returncode, stdout, stderr = run_gpio_tool(['-1'], env=test_env)
    assert returncode == 1
    error_msg = stderr + stdout
    assert "out of valid range" in error_msg
    print("✓ Negative pin test passed")

@test
def test_pin_too_high():
    test_env = {'JETSON_TESTING_MODEL_NAME': 'JETSON_ORIN'}
    returncode, stdout, stderr = run_gpio_tool(['41'], env=test_env)
    assert returncode == 1
    error_msg = stderr + stdout
    assert "out of valid range" in error_msg
    print("✓ Pin number too high test passed")

# Tests for different Jetson models

@test
def test_jetson_orin_valid_pins():
    test_env = {'JETSON_TESTING_MODEL_NAME': 'JETSON_ORIN'}
    failed = False
    
    # Test all valid GPIO pins for Jetson Orin
    for gpio_pin in test_data['JETSON_ORIN']['expected_addresses'].keys():
        returncode, stdout, stderr = run_gpio_tool([str(gpio_pin)], env=test_env)
        assert returncode == 0
        assert f"GPIO Pin {gpio_pin}:" in stdout
        assert "Mux Register Address" in stdout
        if f"{test_data['JETSON_ORIN']['expected_addresses'][gpio_pin]:X}" not in stdout:
            print(f"Jetson Orin GPIO pin {gpio_pin} test failed! Expected {test_data['JETSON_ORIN']['expected_addresses'][gpio_pin]:X}")
            failed = True
        else:
            print(f"✓ Jetson Orin GPIO pin {gpio_pin} test passed")

    assert not failed

@test
def test_jetson_orin_nx_valid_pins():
    test_env = {'JETSON_TESTING_MODEL_NAME': 'JETSON_ORIN_NX'}
    failed = False

    # Test all valid GPIO pins for Jetson Orin NX
    for gpio_pin in test_data['JETSON_ORIN_NX']['expected_addresses'].keys():
        returncode, stdout, stderr = run_gpio_tool([str(gpio_pin)], env=test_env)
        assert returncode == 0
        assert f"GPIO Pin {gpio_pin}:" in stdout
        assert "Mux Register Address" in stdout
        if f"{test_data['JETSON_ORIN_NX']['expected_addresses'][gpio_pin]:X}" not in stdout:
            print(f"Jetson Orin NX GPIO pin {gpio_pin} test failed! Expected {test_data['JETSON_ORIN_NX']['expected_addresses'][gpio_pin]:X}")
            failed = True
        else:
            print(f"✓ Jetson Orin NX GPIO pin {gpio_pin} test passed")
            
    assert not failed

@test
def test_jetson_orin_nano_valid_pins():
    test_env = {'JETSON_TESTING_MODEL_NAME': 'JETSON_ORIN_NANO'}
    failed = False
    
    # Test all valid GPIO pins for Jetson Orin Nano
    for gpio_pin in test_data['JETSON_ORIN_NX']['expected_addresses'].keys():
        returncode, stdout, stderr = run_gpio_tool([str(gpio_pin)], env=test_env)
        assert returncode == 0
        assert f"GPIO Pin {gpio_pin}:" in stdout
        assert "Mux Register Address" in stdout
        if f"{test_data['JETSON_ORIN_NX']['expected_addresses'][gpio_pin]:X}" not in stdout:
            print(f"Jetson Orin Nano GPIO pin {gpio_pin} test failed! Expected {test_data['JETSON_ORIN_NX']['expected_addresses'][gpio_pin]:X}")
            failed = True
        else:
            print(f"✓ Jetson Orin Nano GPIO pin {gpio_pin} test passed")
            
    assert not failed

# Tests for invalid pins

@test
def test_invalid_pins_jetson_orin():
    test_env = {'JETSON_TESTING_MODEL_NAME': 'JETSON_ORIN'}
    
    # Test a few invalid pins
    for pin in [1, 2, 3, 4, 5, 6]:
        returncode, stdout, stderr = run_gpio_tool([str(pin)], env=test_env)
        assert returncode == 1
        assert f"GPIO pin {pin} not found" in stderr
        print(f"✓ Jetson Orin invalid pin {pin} test passed")

# Test model detection without environment variable

@test
def test_no_model_environment():
    # Remove model environment variable
    test_env = {k: v for k, v in os.environ.items() if k != 'JETSON_TESTING_MODEL_NAME'}
    
    returncode, stdout, stderr = run_gpio_tool(['7'], env=test_env)
    
    # Tool should either detect a model from device tree or fail gracefully
    assert returncode in [0, 1]
    if returncode == 0:
        assert "GPIO Pin 7:" in stdout
    else:
        error_msg = stderr + stdout
        assert "Could not determine Jetson model" in error_msg

    print("✓ No model environment test passed")

# Main test runner

def run_all_tests():
    # Run all tests and report results.
    print("=" * 60)
    print("GPIO Pinmux Lookup Tool - Test Suite")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        print(f"\nRunning {test_func.__name__}:")
        try:
            test_func()
            passed += 1
            print(f"✓ {test_func.__name__} PASSED")
        except Exception as e:
            failed += 1
            print(f"✗ {test_func.__name__} FAILED: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0)

if __name__ == '__main__':
    run_all_tests()
