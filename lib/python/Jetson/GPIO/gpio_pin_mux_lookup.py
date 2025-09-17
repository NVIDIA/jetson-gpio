# Jetson Orin GPIO Pin Mux Register Lookup Tool

# Simple tool to lookup pin mux register address for GPIO pins.
# User must to specify the BOARD mode GPIO pin number.

# Usage:
#     python3 gpio_pin_mux_lookup.py <gpio_pin_number>


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
            return pin_def[9] + pin_def[10]
    
    return -1

# @brief Main function to handle command line interface.
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 gpio_pin_mux_lookup.py <gpio_pin_number>")
        print("\nLookup pin mux register address for GPIO pins.")
        print("Specify the Board Mode GPIO pin number (e.g., 7, 11, 40, etc.)")
        print("\nExample:")
        print("  python3 gpio_pin_mux_lookup.py 7")
        sys.exit(1)
    
    try:
        gpio_pin = int(sys.argv[1])
    except ValueError:
        print(f"Error: GPIO pin number must be an integer, got '{sys.argv[1]}'", file=sys.stderr)
        sys.exit(1)

    model = gpio_pin_data.get_model()
    pin_defs = gpio_pin_data.jetson_gpio_data[model][0]
    
    # Validate GPIO pin range (basic sanity check)
    if gpio_pin < 0 or gpio_pin > 40:
        print(f"Error: GPIO pin number {gpio_pin} is out of valid range (0-40)", file=sys.stderr)
        sys.exit(1)
    
    # Get pin register address
    pin_register_address = lookup_mux_register(gpio_pin, pin_defs)
    
    if pin_register_address == -1:
        print(f"Error: GPIO pin {gpio_pin} not found in {model} pin definitions", file=sys.stderr)
        sys.exit(1)


    print(f"GPIO Pin {gpio_pin}: Mux Register Address = 0x{pin_register_address}")

if __name__ == '__main__':
    main()
