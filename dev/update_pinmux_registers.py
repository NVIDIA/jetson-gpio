#!/usr/bin/env python
# Copyright (c) 2025, NVIDIA CORPORATION. All rights reserved.
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

# @File name: update_pinmux_registers.py
# @Date:
# @Last modified by:
# @Last Modified time: 9/23/2025
# @Description: Update pin_data_file JETSON_ORIN_PIN_DEFS and JETSON_ORIN_NX_PIN_DEFS with correct pinmux registers. Extracts data from tegra234_groups and tegra234_aon_groups in pinctrl file.


import sys
import re

JETSON_ORIN_BASE = 0x02430000
JETSON_ORIN_AON_BASE = 0x0C300000


def extract_pingroup_data_from_pinctrl_file(pinctrl_file):
    pinmux_data = {}
    
    with open(pinctrl_file, 'r') as f:
        content = f.read()
    
    # Remove comments to avoid parsing issues
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Find all PINGROUP entries in both tegra234_groups and tegra234_aon_groups
    # Pattern: PINGROUP(pg_name, f0, f1, f2, f3, r, bank, ...)
    pingroup_pattern = r'PINGROUP\s*\(\s*([a-zA-Z0-9_]+)\s*,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*(0x[0-9a-fA-F]+)'
    
    # Find the tegra234_groups data structure definition
    start = content.find('tegra234_groups[] = {')
    if start == -1:
        print(f"Error: tegra234_groups not found")
        return False
    
    # Find the end of the structure
    bracket_count = 0
    end = start
    for i, char in enumerate(content[start:], start):
        if char == '{':
            bracket_count += 1
        elif char == '}':
            bracket_count -= 1
            if bracket_count == 0:
                end = i
                break
    
    # Process each PINGROUP in the structure
    array_content = content[start:end + 1]
    
    for match in re.finditer(pingroup_pattern, array_content):
        pg_name, reg_offset = match.groups()
        # remove everything before the last _ in pg_name
        pg_name = pg_name.rsplit('_', 1)[1]
        pinmux_data[pg_name] = int(reg_offset, 16) + JETSON_ORIN_BASE
    

    # Do the same for tegra234_aon_groups
    # Find the tegra234_aon_groups data structure definition
    start = content.find('tegra234_aon_groups[] = {')
    if start == -1:
        print(f"Error: tegra234_aon_groups not found")
        return False
    
    # Find the end of the structure
    bracket_count = 0
    end = start
    for i, char in enumerate(content[start:], start):
        if char == '{':
            bracket_count += 1
        elif char == '}':
            bracket_count -= 1
            if bracket_count == 0:
                end = i
                break
    
    # Process each PINGROUP in the structure
    array_content = content[start:end + 1]
    
    for match in re.finditer(pingroup_pattern, array_content):
        pg_name, reg_offset = match.groups()
        # remove everything before the last _ in pg_name
        pg_name = pg_name.rsplit('_', 1)[1]
        pinmux_data[pg_name] = int(reg_offset, 16) + JETSON_ORIN_AON_BASE
    
    return pinmux_data

def update_pin_definitions(pin_data_file, pinmux_data, model_name):
    # Update array with correct register offsets.
    with open(pin_data_file, 'r') as f:
        content = f.read()
    
    # Find the array definition
    start = content.find(f'JETSON_{model_name}_PIN_DEFS = [')
    if start == -1:
        print(f"Error: JETSON_{model_name}_PIN_DEFS array not found")
        return False
    
    # Find the end of the array
    bracket_count = 0
    end = start
    for i, char in enumerate(content[start:], start):
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end = i
                break
    
    # Process each tuple in the array
    array_content = content[start:end + 1]
    updated_content = array_content
    
    # Find and update each tuple
    for match in re.finditer(r'\(([^)]+)\)', array_content):
        tuple_content = match.group(1)
        parts = [p.strip() for p in tuple_content.split(',')]
        
        if len(parts) >= 10:
            # Get pin name from index 1, remove quotes and periods, make lowercase
            pin_name = parts[1].strip("'\"").replace('.', '').lower()

            # Remove leading 0s
            if pin_name[-2] == '0':
                pin_name = pin_name[:-2] + pin_name[-1]
            
            if pin_name and pin_name in pinmux_data:
                # Update the last column (register offset) from pinmux_data
                parts[-1] = f'0x{pinmux_data[pin_name]:X}'
                
                # Replace the tuple
                new_tuple = '(' + ', '.join(parts) + ')'
                updated_content = updated_content.replace(match.group(0), new_tuple)
                print(f"Updated {pin_name}: 0x{pinmux_data[pin_name]:X}")
            else:
                if pin_name:
                    print(f"Warning: No pinmux data found for {pin_name}")
                else:
                    print(f"Warning: Could not map pin name {pin_name}")
    
    # Write the updated content back
    new_content = content[:start] + updated_content + content[end + 1:]
    with open(pin_data_file, 'w') as f:
        f.write(new_content)
    
    return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 update_pinmux_registers.py <pinctrl_file> <pin_data_file>")
        print("Example: python3 update_pinmux_registers.py pinctrl-tegra234.c lib/python/Jetson/GPIO/gpio_pin_data.py")
        sys.exit(1)
    
    pinctrl_file, pin_data_file = sys.argv[1], sys.argv[2]
    
    print(f"Extracting pinmux data from {pinctrl_file} using regex parsing...")
    pinmux_data = extract_pingroup_data_from_pinctrl_file(pinctrl_file)
    print(f"Found {len(pinmux_data)} pinmux entries in tegra234_groups and tegra234_aon_groups")
    
    print("Updating pin definitions...")
    if update_pin_definitions(pin_data_file, pinmux_data, "ORIN_NX") and update_pin_definitions(pin_data_file, pinmux_data, "ORIN"):
        print("Successfully updated pin definitions!")
    else:
        print("Failed to update pin definitions")
        sys.exit(1)

if __name__ == '__main__':
    main()