#!/usr/bin/env python3

from __future__ import print_function
import os
import sys
import subprocess
import tempfile

# Add the lib/python directory to Python path
sys.path.insert(0, os.path.abspath('../lib/python'))

# Import gpio_pin_data directly to avoid GPIO hardware checks
import importlib.util
spec = importlib.util.spec_from_file_location("gpio_pin_data", 
                                             os.path.abspath('../lib/python/Jetson/GPIO/gpio_pin_data.py'))
gpio_pin_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gpio_pin_data)

# Test data for different Jetson models
test_data = {
    'JETSON_ORIN': {
        'expected_addresses': {
            7: 0x02430070,   # GPIO pin 106: PQ.06
            11: 0x02430098,  # GPIO pin 112: PR.04  
            12: 0x02434088,  # GPIO pin 50: PH.07
        }
    },
    'JETSON_ORIN_NX': {
        'expected_addresses': {
            7: 0x02448028,   # GPIO pin 144: PAC.06
            11: 0x02430098,  # GPIO pin 112: PR.04
            12: 0x02434088,  # GPIO pin 50: PH.07
        }
    },
    'JETSON_ORIN_NANO': {
        'expected_addresses': {
            7: 0x02448028,   # GPIO pin 144: PAC.06
            11: 0x02430098,  # GPIO pin 112: PR.04
            12: 0x02434088,  # GPIO pin 50: PH.07
        }
    }
}

tests = []

def test(f):
    tests.append(f)
    return f

# Get the path to the gpio_pin_mux_lookup.py script
script_path = os.path.join('..', 'lib', 'python', 'Jetson', 'GPIO', 'gpio_pin_mux_lookup.py')

def run_gpio_tool(args, env=None):
    """Helper function to run the GPIO pin mux lookup tool."""
    cmd = [sys.executable, script_path] + args
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
    assert "gpio_pin_mux_lookup.py <gpio_pin_number>" in stdout
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
    test_env = {'JETSON_MODEL_NAME': 'JETSON_ORIN'}
    returncode, stdout, stderr = run_gpio_tool(['-1'], env=test_env)
    assert returncode == 1
    error_msg = stderr + stdout
    assert "out of valid range" in error_msg
    print("✓ Negative pin test passed")

@test
def test_pin_too_high():
    test_env = {'JETSON_MODEL_NAME': 'JETSON_ORIN'}
    returncode, stdout, stderr = run_gpio_tool(['41'], env=test_env)
    assert returncode == 1
    error_msg = stderr + stdout
    assert "out of valid range" in error_msg
    print("✓ Pin number too high test passed")

# Tests for different Jetson models

@test
def test_jetson_orin_valid_pins():
    test_env = {'JETSON_MODEL_NAME': 'JETSON_ORIN'}
    
    for pin in [7, 11, 12]:  # Test a few key pins
        returncode, stdout, stderr = run_gpio_tool([str(pin)], env=test_env)
        assert returncode == 0
        assert f"GPIO Pin {pin}:" in stdout
        assert "Mux Register Address" in stdout
        assert f"{test_data['JETSON_ORIN']['expected_addresses'][pin]}" in stdout 
        print(f"✓ Jetson Orin pin {pin} test passed")

@test
def test_jetson_orin_nx_valid_pins():
    test_env = {'JETSON_MODEL_NAME': 'JETSON_ORIN_NX'}
    
    for pin in [7, 11, 12]:
        returncode, stdout, stderr = run_gpio_tool([str(pin)], env=test_env)
        assert returncode == 0
        assert f"GPIO Pin {pin}:" in stdout
        assert "Mux Register Address" in stdout
        assert f"{test_data['JETSON_ORIN_NX']['expected_addresses'][pin]}" in stdout
        print(f"✓ Jetson Orin NX pin {pin} test passed")

@test
def test_jetson_orin_nano_valid_pins():
    test_env = {'JETSON_MODEL_NAME': 'JETSON_ORIN_NANO'}
    
    for pin in [7, 11, 12]:
        returncode, stdout, stderr = run_gpio_tool([str(pin)], env=test_env)
        assert returncode == 0
        assert f"GPIO Pin {pin}:" in stdout
        assert "Mux Register Address" in stdout
        assert f"{test_data['JETSON_ORIN_NANO']['expected_addresses'][pin]}" in stdout
        print(f"✓ Jetson Orin Nano pin {pin} test passed")

# Tests for invalid pins -- TODO: Look past here

@test
def test_invalid_pins_jetson_orin():
    test_env = {'JETSON_MODEL_NAME': 'JETSON_ORIN'}
    
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
    test_env = {k: v for k, v in os.environ.items() if k != 'JETSON_MODEL_NAME'}
    
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
    print("GPIO Pin Mux Lookup Tool - Test Suite")
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
