# Copyright (c) 2018-2020, NVIDIA CORPORATION. All rights reserved.
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
import os.path
import sys

JETSON_NX = 'JETSON_NX'
JETSON_XAVIER = 'JETSON_XAVIER'
JETSON_TX2 = 'JETSON_TX2'
JETSON_TX1 = 'JETSON_TX1'
JETSON_NANO = 'JETSON_NANO'

# These arrays contain tuples of all the relevant GPIO data for each Jetson
# Platform. The fields are:
# - Linux GPIO pin number,
# - GPIO chip sysfs directory
# - Pin number (BOARD mode)
# - Pin number (BCM mode)
# - Pin name (CVM mode)
# - Pin name (TEGRA_SOC mode)
# - PWM chip sysfs directory
# - PWM ID within PWM chip
# The values are use to generate dictionaries that map the corresponding pin
# mode numbers to the Linux GPIO pin number and GPIO chip directory
JETSON_NX_PIN_DEFS = [
    (148, "/sys/devices/2200000.gpio", 7, 4, 'GPIO09', 'AUD_MCLK', None, None),
    (140, "/sys/devices/2200000.gpio", 11, 17, 'UART1_RTS', 'UART1_RTS', None, None),
    (157, "/sys/devices/2200000.gpio", 12, 18, 'I2S0_SCLK', 'DAP5_SCLK', None, None),
    (192, "/sys/devices/2200000.gpio", 13, 27, 'SPI1_SCK', 'SPI3_SCK', None, None),
    (20, "/sys/devices/c2f0000.gpio", 15, 22, 'GPIO12', 'TOUCH_CLK', None, None),
    (196, "/sys/devices/2200000.gpio", 16, 23, 'SPI1_CS1', 'SPI3_CS1_N', None, None),
    (195, "/sys/devices/2200000.gpio", 18, 24, 'SPI1_CS0', 'SPI3_CS0_N', None, None),
    (205, "/sys/devices/2200000.gpio", 19, 10, 'SPI0_MOSI', 'SPI1_MOSI', None, None),
    (204, "/sys/devices/2200000.gpio", 21, 9, 'SPI0_MISO', 'SPI1_MISO', None, None),
    (193, "/sys/devices/2200000.gpio", 22, 25, 'SPI1_MISO', 'SPI3_MISO', None, None),
    (203, "/sys/devices/2200000.gpio", 23, 11, 'SPI0_SCK', 'SPI1_SCK', None, None),
    (206, "/sys/devices/2200000.gpio", 24, 8, 'SPI0_CS0', 'SPI1_CS0_N', None, None),
    (207, "/sys/devices/2200000.gpio", 26, 7, 'SPI0_CS1', 'SPI1_CS1_N', None, None),
    (133, "/sys/devices/2200000.gpio", 29, 5, 'GPIO01', 'SOC_GPIO41', None, None),
    (134, "/sys/devices/2200000.gpio", 31, 6, 'GPIO11', 'SOC_GPIO42', None, None),
    (136, "/sys/devices/2200000.gpio", 32, 12, 'GPIO07', 'SOC_GPIO44', '/sys/devices/32f0000.pwm', 0),
    (105, "/sys/devices/2200000.gpio", 33, 13, 'GPIO13', 'SOC_GPIO54', '/sys/devices/3280000.pwm', 0),
    (160, "/sys/devices/2200000.gpio", 35, 19, 'I2S0_FS', 'DAP5_FS', None, None),
    (141, "/sys/devices/2200000.gpio", 36, 16, 'UART1_CTS', 'UART1_CTS', None, None),
    (194, "/sys/devices/2200000.gpio", 37, 26, 'SPI1_MOSI', 'SPI3_MOSI', None, None),
    (159, "/sys/devices/2200000.gpio", 38, 20, 'I2S0_DIN', 'DAP5_DIN', None, None),
    (158, "/sys/devices/2200000.gpio", 40, 21, 'I2S0_DOUT', 'DAP5_DOUT', None, None)
]
compats_nx = (
    'nvidia,p3509-0000+p3668-0000',
    'nvidia,p3509-0000+p3668-0001',
    'nvidia,p3449-0000+p3668-0000',
    'nvidia,p3449-0000+p3668-0001',
)

JETSON_XAVIER_PIN_DEFS = [
    (134, "/sys/devices/2200000.gpio", 7, 4, 'MCLK05', 'SOC_GPIO42', None, None),
    (140, "/sys/devices/2200000.gpio", 11, 17, 'UART1_RTS', 'UART1_RTS', None, None),
    (63, "/sys/devices/2200000.gpio", 12, 18, 'I2S2_CLK', 'DAP2_SCLK', None, None),
    (136, "/sys/devices/2200000.gpio", 13, 27, 'PWM01', 'SOC_GPIO44', '/sys/devices/32f0000.pwm', 0),
    # Older versions of L4T don't enable this PWM controller in DT, so this PWM
    # channel may not be available.
    (105, "/sys/devices/2200000.gpio", 15, 22, 'GPIO27', 'SOC_GPIO54', '/sys/devices/3280000.pwm', 0),
    (8, "/sys/devices/c2f0000.gpio", 16, 23, 'GPIO8', 'CAN1_STB', None, None),
    (56, "/sys/devices/2200000.gpio", 18, 24, 'GPIO35', 'SOC_GPIO12', '/sys/devices/32c0000.pwm', 0),
    (205, "/sys/devices/2200000.gpio", 19, 10, 'SPI1_MOSI', 'SPI1_MOSI', None, None),
    (204, "/sys/devices/2200000.gpio", 21, 9, 'SPI1_MISO', 'SPI1_MISO', None, None),
    (129, "/sys/devices/2200000.gpio", 22, 25, 'GPIO17', 'SOC_GPIO21', None, None),
    (203, "/sys/devices/2200000.gpio", 23, 11, 'SPI1_CLK', 'SPI1_SCK', None, None),
    (206, "/sys/devices/2200000.gpio", 24, 8, 'SPI1_CS0_N', 'SPI1_CS0_N', None, None),
    (207, "/sys/devices/2200000.gpio", 26, 7, 'SPI1_CS1_N', 'SPI1_CS1_N', None, None),
    (3, "/sys/devices/c2f0000.gpio", 29, 5, 'CAN0_DIN', 'CAN0_DIN', None, None),
    (2, "/sys/devices/c2f0000.gpio", 31, 6, 'CAN0_DOUT', 'CAN0_DOUT', None, None),
    (9, "/sys/devices/c2f0000.gpio", 32, 12, 'GPIO9', 'CAN1_EN', None, None),
    (0, "/sys/devices/c2f0000.gpio", 33, 13, 'CAN1_DOUT', 'CAN1_DOUT', None, None),
    (66, "/sys/devices/2200000.gpio", 35, 19, 'I2S2_FS', 'DAP2_FS', None, None),
    # Input-only (due to base board)
    (141, "/sys/devices/2200000.gpio", 36, 16, 'UART1_CTS', 'UART1_CTS', None, None),
    (1, "/sys/devices/c2f0000.gpio", 37, 26, 'CAN1_DIN', 'CAN1_DIN', None, None),
    (65, "/sys/devices/2200000.gpio", 38, 20, 'I2S2_DIN', 'DAP2_DIN', None, None),
    (64, "/sys/devices/2200000.gpio", 40, 21, 'I2S2_DOUT', 'DAP2_DOUT', None, None)
]
compats_xavier = (
    'nvidia,p2972-0000',
    'nvidia,p2972-0006',
    'nvidia,jetson-xavier',
)

JETSON_TX2_PIN_DEFS = [
    (76, "/sys/devices/2200000.gpio", 7, 4, 'AUDIO_MCLK', 'AUD_MCLK', None, None),
    # Output-only (due to base board)
    (146, "/sys/devices/2200000.gpio", 11, 17, 'UART0_RTS', 'UART1_RTS', None, None),
    (72, "/sys/devices/2200000.gpio", 12, 18, 'I2S0_CLK', 'DAP1_SCLK', None, None),
    (77, "/sys/devices/2200000.gpio", 13, 27, 'GPIO20_AUD_INT', 'GPIO_AUD0', None, None),
    (15, "/sys/devices/3160000.i2c/i2c-0/0-0074", 15, 22, 'GPIO_EXP_P17', 'GPIO_EXP_P17', None, None),
    # Input-only (due to module):
    (40, "/sys/devices/c2f0000.gpio", 16, 23, 'AO_DMIC_IN_DAT', 'CAN_GPIO0', None, None),
    (161, "/sys/devices/2200000.gpio", 18, 24, 'GPIO16_MDM_WAKE_AP', 'GPIO_MDM2', None, None),
    (109, "/sys/devices/2200000.gpio", 19, 10, 'SPI1_MOSI', 'GPIO_CAM6', None, None),
    (108, "/sys/devices/2200000.gpio", 21, 9, 'SPI1_MISO', 'GPIO_CAM5', None, None),
    (14, "/sys/devices/3160000.i2c/i2c-0/0-0074", 22, 25, 'GPIO_EXP_P16', 'GPIO_EXP_P16', None, None),
    (107, "/sys/devices/2200000.gpio", 23, 11, 'SPI1_CLK', 'GPIO_CAM4', None, None),
    (110, "/sys/devices/2200000.gpio", 24, 8, 'SPI1_CS0', 'GPIO_CAM7', None, None),
    (None, None, 26, 7, 'SPI1_CS1', None, None, None),
    (78, "/sys/devices/2200000.gpio", 29, 5, 'GPIO19_AUD_RST', 'GPIO_AUD1', None, None),
    (42, "/sys/devices/c2f0000.gpio", 31, 6, 'GPIO9_MOTION_INT', 'CAN_GPIO2', None, None),
    # Output-only (due to module):
    (41, "/sys/devices/c2f0000.gpio", 32, 12, 'AO_DMIC_IN_CLK', 'CAN_GPIO1', None, None),
    (69, "/sys/devices/2200000.gpio", 33, 13, 'GPIO11_AP_WAKE_BT', 'GPIO_PQ5', None, None),
    (75, "/sys/devices/2200000.gpio", 35, 19, 'I2S0_LRCLK', 'DAP1_FS', None, None),
    # Input-only (due to base board) IF NVIDIA debug card NOT plugged in
    # Output-only (due to base board) IF NVIDIA debug card plugged in
    (147, "/sys/devices/2200000.gpio", 36, 16, 'UART0_CTS', 'UART1_CTS', None, None),
    (68, "/sys/devices/2200000.gpio", 37, 26, 'GPIO8_ALS_PROX_INT', 'GPIO_PQ4', None, None),
    (74, "/sys/devices/2200000.gpio", 38, 20, 'I2S0_SDIN', 'DAP1_DIN', None, None),
    (73, "/sys/devices/2200000.gpio", 40, 21, 'I2S0_SDOUT', 'DAP1_DOUT', None, None)
]
compats_tx2 = (
    'nvidia,p2771-0000',
    'nvidia,p2771-0888',
    'nvidia,p3489-0000',
    'nvidia,lightning',
    'nvidia,quill',
    'nvidia,storm',
)

JETSON_TX1_PIN_DEFS = [
    (216, "/sys/devices/6000d000.gpio", 7, 4, 'AUDIO_MCLK', 'AUD_MCLK', None, None),
    # Output-only (due to base board)
    (162, "/sys/devices/6000d000.gpio", 11, 17, 'UART0_RTS', 'UART1_RTS', None, None),
    (11, "/sys/devices/6000d000.gpio", 12, 18, 'I2S0_CLK', 'DAP1_SCLK', None, None),
    (38, "/sys/devices/6000d000.gpio", 13, 27, 'GPIO20_AUD_INT', 'GPIO_PE6', None, None),
    (15, "/sys/devices/7000c400.i2c/i2c-1/1-0074", 15, 22, 'GPIO_EXP_P17', 'GPIO_EXP_P17', None, None),
    (37, "/sys/devices/6000d000.gpio", 16, 23, 'AO_DMIC_IN_DAT', 'DMIC3_DAT', None, None),
    (184, "/sys/devices/6000d000.gpio", 18, 24, 'GPIO16_MDM_WAKE_AP', 'MODEM_WAKE_AP', None, None),
    (16, "/sys/devices/6000d000.gpio", 19, 10, 'SPI1_MOSI', 'SPI1_MOSI', None, None),
    (17, "/sys/devices/6000d000.gpio", 21, 9, 'SPI1_MISO', 'SPI1_MISO', None, None),
    (14, "/sys/devices/7000c400.i2c/i2c-1/1-0074", 22, 25, 'GPIO_EXP_P16', 'GPIO_EXP_P16', None, None),
    (18, "/sys/devices/6000d000.gpio", 23, 11, 'SPI1_CLK', 'SPI1_SCK', None, None),
    (19, "/sys/devices/6000d000.gpio", 24, 8, 'SPI1_CS0', 'SPI1_CS0', None, None),
    (20, "/sys/devices/6000d000.gpio", 26, 7, 'SPI1_CS1', 'SPI1_CS1', None, None),
    (219, "/sys/devices/6000d000.gpio", 29, 5, 'GPIO19_AUD_RST', 'GPIO_X1_AUD', None, None),
    (186, "/sys/devices/6000d000.gpio", 31, 6, 'GPIO9_MOTION_INT', 'MOTION_INT', None, None),
    (36, "/sys/devices/6000d000.gpio", 32, 12, 'AO_DMIC_IN_CLK', 'DMIC3_CLK', None, None),
    (63, "/sys/devices/6000d000.gpio", 33, 13, 'GPIO11_AP_WAKE_BT', 'AP_WAKE_NFC', None, None),
    (8, "/sys/devices/6000d000.gpio", 35, 19, 'I2S0_LRCLK', 'DAP1_FS', None, None),
    # Input-only (due to base board) IF NVIDIA debug card NOT plugged in
    # Input-only (due to base board) (always reads fixed value) IF NVIDIA debug card plugged in
    (163, "/sys/devices/6000d000.gpio", 36, 16, 'UART0_CTS', 'UART1_CTS', None, None),
    (187, "/sys/devices/6000d000.gpio", 37, 26, 'GPIO8_ALS_PROX_INT', 'ALS_PROX_INT', None, None),
    (9, "/sys/devices/6000d000.gpio", 38, 20, 'I2S0_SDIN', 'DAP1_DIN', None, None),
    (10, "/sys/devices/6000d000.gpio", 40, 21, 'I2S0_SDOUT', 'DAP1_DOUT', None, None)
]
compats_tx1 = (
    'nvidia,p2371-2180',
    'nvidia,jetson-cv',
)

JETSON_NANO_PIN_DEFS = [
    (216, "/sys/devices/6000d000.gpio", 7, 4, 'GPIO9', 'AUD_MCLK', None, None),
    (50, "/sys/devices/6000d000.gpio", 11, 17, 'UART1_RTS', 'UART2_RTS', None, None),
    (79, "/sys/devices/6000d000.gpio", 12, 18, 'I2S0_SCLK', 'DAP4_SCLK', None, None),
    (14, "/sys/devices/6000d000.gpio", 13, 27, 'SPI1_SCK', 'SPI2_SCK', None, None),
    (194, "/sys/devices/6000d000.gpio", 15, 22, 'GPIO12', 'LCD_TE', None, None),
    (232, "/sys/devices/6000d000.gpio", 16, 23, 'SPI1_CS1', 'SPI2_CS1', None, None),
    (15, "/sys/devices/6000d000.gpio", 18, 24, 'SPI1_CS0', 'SPI2_CS0', None, None),
    (16, "/sys/devices/6000d000.gpio", 19, 10, 'SPI0_MOSI', 'SPI1_MOSI', None, None),
    (17, "/sys/devices/6000d000.gpio", 21, 9, 'SPI0_MISO', 'SPI1_MISO', None, None),
    (13, "/sys/devices/6000d000.gpio", 22, 25, 'SPI1_MISO', 'SPI2_MISO', None, None),
    (18, "/sys/devices/6000d000.gpio", 23, 11, 'SPI0_SCK', 'SPI1_SCK', None, None),
    (19, "/sys/devices/6000d000.gpio", 24, 8, 'SPI0_CS0', 'SPI1_CS0', None, None),
    (20, "/sys/devices/6000d000.gpio", 26, 7, 'SPI0_CS1', 'SPI1_CS1', None, None),
    (149, "/sys/devices/6000d000.gpio", 29, 5, 'GPIO01', 'CAM_AF_EN', None, None),
    (200, "/sys/devices/6000d000.gpio", 31, 6, 'GPIO11', 'GPIO_PZ0', None, None),
    # Older versions of L4T have a DT bug which instantiates a bogus device
    # which prevents this library from using this PWM channel.
    (168, "/sys/devices/6000d000.gpio", 32, 12, 'GPIO07', 'LCD_BL_PW', '/sys/devices/7000a000.pwm', 0),
    (38, "/sys/devices/6000d000.gpio", 33, 13, 'GPIO13', 'GPIO_PE6', '/sys/devices/7000a000.pwm', 2),
    (76, "/sys/devices/6000d000.gpio", 35, 19, 'I2S0_FS', 'DAP4_FS', None, None),
    (51, "/sys/devices/6000d000.gpio", 36, 16, 'UART1_CTS', 'UART2_CTS', None, None),
    (12, "/sys/devices/6000d000.gpio", 37, 26, 'SPI1_MOSI', 'SPI2_MOSI', None, None),
    (77, "/sys/devices/6000d000.gpio", 38, 20, 'I2S0_DIN', 'DAP4_DIN', None, None),
    (78, "/sys/devices/6000d000.gpio", 40, 21, 'I2S0_DOUT', 'DAP4_DOUT', None, None)
]
compats_nano = (
    'nvidia,p3450-0000',
    'nvidia,p3450-0002',
    'nvidia,jetson-nano',
)

jetson_gpio_data = {
    JETSON_NX: (
        JETSON_NX_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '16384M',
            'REVISION': 'Unknown',
            'TYPE': 'Jetson NX',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'ARM Carmel'
        }
    ),
    JETSON_XAVIER: (
        JETSON_XAVIER_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '16384M',
            'REVISION': 'Unknown',
            'TYPE': 'Jetson Xavier',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'ARM Carmel'
        }
    ),
    JETSON_TX2: (
        JETSON_TX2_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '8192M',
            'REVISION': 'Unknown',
            'TYPE': 'Jetson TX2',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'ARM A57 + Denver'
        }
    ),
    JETSON_TX1: (
        JETSON_TX1_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '4096M',
            'REVISION': 'Unknown',
            'TYPE': 'Jetson TX1',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'ARM A57'
        }
    ),
    JETSON_NANO: (
        JETSON_NANO_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '4096M',
            'REVISION': 'Unknown',
            'TYPE': 'Jetson Nano',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'ARM A57'
        }
    ),
}


class ChannelInfo(object):
    def __init__(self, channel, gpio_chip_dir, chip_gpio, gpio, pwm_chip_dir, pwm_id):
        self.channel = channel
        self.gpio_chip_dir = gpio_chip_dir
        self.chip_gpio = chip_gpio
        self.gpio = gpio
        self.pwm_chip_dir = pwm_chip_dir
        self.pwm_id = pwm_id


ids_warned = False


def get_data():
    compatible_path = '/proc/device-tree/compatible'
    ids_path = '/proc/device-tree/chosen/plugin-manager/ids'

    with open(compatible_path, 'r') as f:
        compatibles = f.read().split('\x00')

    def matches(vals):
        return any(v in compatibles for v in vals)

    def find_pmgr_board(prefix):
        global ids_warned
        if not os.path.exists(ids_path):
            if not ids_warned:
                ids_warned = True
                msg = """\
WARNING: Plugin manager information missing from device tree.
WARNING: Cannot determine whether the expected Jetson board is present.
"""
                sys.stderr.write(msg)
            return None
        for f in os.listdir(ids_path):
            if f.startswith(prefix):
                return f
        return None

    def warn_if_not_carrier_board(*carrier_boards):
        found = False
        for b in carrier_boards:
            found = find_pmgr_board(b + '-')
            if found:
                break
        if not found:
            msg = """\
WARNING: Carrier board is not from a Jetson Developer Kit.
WARNNIG: Jetson.GPIO library has not been verified with this carrier board,
WARNING: and in fact is unlikely to work correctly.
"""
            sys.stderr.write(msg)

    if matches(compats_tx1):
        model = JETSON_TX1
        warn_if_not_carrier_board('2597')
    elif matches(compats_tx2):
        model = JETSON_TX2
        warn_if_not_carrier_board('2597')
    elif matches(compats_xavier):
        model = JETSON_XAVIER
        warn_if_not_carrier_board('2822')
    elif matches(compats_nano):
        model = JETSON_NANO
        module_id = find_pmgr_board('3448')
        if not module_id:
            raise Exception('Could not determine Jetson Nano module revision')
        revision = module_id.split('-')[-1]
        # Revision is an ordered string, not a decimal integer
        if revision < "200":
            raise Exception('Jetson Nano module revision must be A02 or later')
        warn_if_not_carrier_board('3449')
    elif matches(compats_nx):
        model = JETSON_NX
        warn_if_not_carrier_board('3509', '3449')
    else:
        raise Exception('Could not determine Jetson model')

    pin_defs, jetson_info = jetson_gpio_data[model]
    gpio_chip_base = {}
    pwm_dirs = {}

    # Get the gpiochip offsets
    gpio_chip_dirs = set([x[1] for x in pin_defs if x[1] is not None])
    for gpio_chip_dir in gpio_chip_dirs:
        gpio_chip_gpio_dir = gpio_chip_dir + '/gpio'
        for fn in os.listdir(gpio_chip_gpio_dir):
            if not fn.startswith('gpiochip'):
                continue
            gpiochip_fn = gpio_chip_gpio_dir + '/' + fn + '/base'
            with open(gpiochip_fn, 'r') as f:
                gpio_chip_base[gpio_chip_dir] = int(f.read().strip())
                break

    def global_gpio_id(gpio_chip_dir, chip_relative_id):
        if gpio_chip_dir is None or chip_relative_id is None:
            return None
        return gpio_chip_base[gpio_chip_dir] + chip_relative_id

    def pwm_dir(chip_dir):
        if chip_dir is None:
            return None
        if chip_dir in pwm_dirs:
            return pwm_dirs[chip_dir]
        chip_pwm_dir = chip_dir + '/pwm'
        # Some PWM controllers aren't enabled in all versions of the DT. In
        # this case, just hide the PWM function on this pin, but let all other
        # aspects of the library continue to work.
        if not os.path.exists(chip_pwm_dir):
            return None
        for fn in os.listdir(chip_pwm_dir):
            if not fn.startswith('pwmchip'):
                continue
            chip_pwm_pwmchip_dir = chip_pwm_dir + '/' + fn
            pwm_dirs[chip_dir] = chip_pwm_pwmchip_dir
            return chip_pwm_pwmchip_dir
        return None

    def model_data(key_col, pin_defs):
        return {x[key_col]: ChannelInfo(
            x[key_col],
            x[1],
            x[0],
            global_gpio_id(x[1], x[0]),
            pwm_dir(x[6]), x[7]) for x in pin_defs}

    channel_data = {
        'BOARD': model_data(2, pin_defs),
        'BCM': model_data(3, pin_defs),
        'CVM': model_data(4, pin_defs),
        'TEGRA_SOC': model_data(5, pin_defs),
    }

    return model, jetson_info, channel_data
