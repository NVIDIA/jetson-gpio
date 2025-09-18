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
import os
import sys
import subprocess

# Test data for different Jetson models
test_data = {
    'JETSON_ORIN': {
        'expected_addresses': {
            # All valid BOARD pins for Jetson Orin (calculated from pin definitions)
            7: 0x02430070,   # GPIO 106: PQ.06 (A0: 0x02430000 + 0x70)
            11: 0x02430098,  # GPIO 112: PR.04 (A0: 0x02430000 + 0x98)
            12: 0x02434088,  # GPIO 50: PH.07 (A4: 0x02434000 + 0x88)
            13: 0x02430080,  # GPIO 108: PR.00 (A0: 0x02430000 + 0x80)
            15: 0x02440020,  # GPIO 85: PN.01 (A16: 0x02440000 + 0x20)
            16: 0x0C302048,  # GPIO 9: PBB.01 (A14: 0x0C302000 + 0x48)
            18: 0x02434040,  # GPIO 43: PH.00 (A4: 0x02434000 + 0x40)
            19: 0x0243D040,  # GPIO 135: PZ.05 (A13: 0x0243D000 + 0x40)
            21: 0x0243D018,  # GPIO 134: PZ.04 (A13: 0x0243D000 + 0x18)
            22: 0x02430020,  # GPIO 96: PP.04 (A0: 0x02430000 + 0x20)
            23: 0x0243D028,  # GPIO 133: PZ.03 (A13: 0x0243D000 + 0x28)
            24: 0x0243D008,  # GPIO 136: PZ.06 (A13: 0x0243D000 + 0x8)
            26: 0x0243D038,  # GPIO 137: PZ.07 (A13: 0x0243D000 + 0x38)
            29: 0x0C302018,  # GPIO 1: PAA.01 (A14: 0x0C302000 + 0x18)
            31: 0x0C302010,  # GPIO 0: PAA.00 (A14: 0x0C302000 + 0x10)
            32: 0x0C302040,  # GPIO 8: PBB.00 (A14: 0x0C302000 + 0x40)
            33: 0x0C302000,  # GPIO 2: PAA.02 (A14: 0x0C302000 + 0x0)
            35: 0x024340A0,  # GPIO 53: PI.02 (A4: 0x02434000 + 0xA0)
            36: 0x02430090,  # GPIO 113: PR.05 (A0: 0x02430000 + 0x90)
            37: 0x0C302008,  # GPIO 3: PAA.03 (A14: 0x0C302000 + 0x8)
            38: 0x02434098,  # GPIO 52: PI.01 (A4: 0x02434000 + 0x98)
            40: 0x02434090,  # GPIO 51: PI.00 (A4: 0x02434000 + 0x90)
        }
    },
    'JETSON_ORIN_NX': {
        'expected_addresses': {
            # All valid BOARD pins for Jetson Orin NX (calculated from pin definitions)
            7: 0x02448028,   # GPIO 144: PAC.06 (A24: 0x02448000 + 0x28)
            11: 0x02430098,  # GPIO 112: PR.04 (A0: 0x02430000 + 0x98)
            12: 0x02434088,  # GPIO 50: PH.07 (A4: 0x02434000 + 0x88)
            13: 0x0243D030,  # GPIO 122: PY.00 (A13: 0x0243D000 + 0x30)
            15: 0x02440020,  # GPIO 85: PN.01 (A16: 0x02440000 + 0x20)
            16: 0x0243D020,  # GPIO 126: PY.04 (A13: 0x0243D000 + 0x20)
            18: 0x0243D010,  # GPIO 125: PY.03 (A13: 0x0243D000 + 0x10)
            19: 0x0243D040,  # GPIO 135: PZ.05 (A13: 0x0243D000 + 0x40)
            21: 0x0243D018,  # GPIO 134: PZ.04 (A13: 0x0243D000 + 0x18)
            22: 0x0243D000,  # GPIO 123: PY.01 (A13: 0x0243D000 + 0x0)
            23: 0x0243D028,  # GPIO 133: PZ.03 (A13: 0x0243D000 + 0x28)
            24: 0x0243D008,  # GPIO 136: PZ.06 (A13: 0x0243D000 + 0x8)
            26: 0x0243D038,  # GPIO 137: PZ.07 (A13: 0x0243D000 + 0x38)
            29: 0x02430068,  # GPIO 105: PQ.05 (A0: 0x02430000 + 0x68)
            31: 0x02430070,  # GPIO 106: PQ.06 (A0: 0x02430000 + 0x70)
            32: 0x02434080,  # GPIO 41: PG.06 (A4: 0x02434000 + 0x80)
            33: 0x02434040,  # GPIO 43: PH.00 (A4: 0x02434000 + 0x40)
            35: 0x024340A0,  # GPIO 53: PI.02 (A4: 0x02434000 + 0xA0)
            36: 0x02430090,  # GPIO 113: PR.05 (A0: 0x02430000 + 0x90)
            37: 0x0243D048,  # GPIO 124: PY.02 (A13: 0x0243D000 + 0x48)
            38: 0x02434098,  # GPIO 52: PI.01 (A4: 0x02434000 + 0x98)
            40: 0x02434090,  # GPIO 51: PI.00 (A4: 0x02434000 + 0x90)
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
    
    # Test all valid GPIO pins for Jetson Orin
    for gpio_pin in test_data['JETSON_ORIN']['expected_addresses'].keys():
        returncode, stdout, stderr = run_gpio_tool([str(gpio_pin)], env=test_env)
        assert returncode == 0
        assert f"GPIO Pin {gpio_pin}:" in stdout
        assert "Mux Register Address" in stdout
        assert f"{test_data['JETSON_ORIN']['expected_addresses'][gpio_pin]:X}" in stdout
        print(f"✓ Jetson Orin GPIO pin {gpio_pin} test passed")

@test
def test_jetson_orin_nx_valid_pins():
    test_env = {'JETSON_TESTING_MODEL_NAME': 'JETSON_ORIN_NX'}
    
    # Test all valid GPIO pins for Jetson Orin NX
    for gpio_pin in test_data['JETSON_ORIN_NX']['expected_addresses'].keys():
        returncode, stdout, stderr = run_gpio_tool([str(gpio_pin)], env=test_env)
        assert returncode == 0
        assert f"GPIO Pin {gpio_pin}:" in stdout
        assert "Mux Register Address" in stdout
        assert f"{test_data['JETSON_ORIN_NX']['expected_addresses'][gpio_pin]:X}" in stdout
        print(f"✓ Jetson Orin NX GPIO pin {gpio_pin} test passed")

@test
def test_jetson_orin_nano_valid_pins():
    test_env = {'JETSON_TESTING_MODEL_NAME': 'JETSON_ORIN_NANO'}
    
    # Test all valid GPIO pins for Jetson Orin Nano
    for gpio_pin in test_data['JETSON_ORIN_NX']['expected_addresses'].keys():
        returncode, stdout, stderr = run_gpio_tool([str(gpio_pin)], env=test_env)
        assert returncode == 0
        assert f"GPIO Pin {gpio_pin}:" in stdout
        assert "Mux Register Address" in stdout
        assert f"{test_data['JETSON_ORIN_NX']['expected_addresses'][gpio_pin]:X}" in stdout
        print(f"✓ Jetson Orin Nano GPIO pin {gpio_pin} test passed")

# Tests for invalid pins -- TODO: Look past here

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
