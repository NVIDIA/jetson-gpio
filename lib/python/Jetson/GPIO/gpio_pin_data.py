# Copyright (c) 2018-2023, NVIDIA CORPORATION. All rights reserved.
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

CLARA_AGX_XAVIER = 'CLARA_AGX_XAVIER'
JETSON_NX = 'JETSON_NX'
JETSON_XAVIER = 'JETSON_XAVIER'
JETSON_TX2 = 'JETSON_TX2'
JETSON_TX1 = 'JETSON_TX1'
JETSON_NANO = 'JETSON_NANO'
JETSON_TX2_NX='JETSON_TX2_NX'
JETSON_ORIN='JETSON_ORIN'
JETSON_ORIN_NX='JETSON_ORIN_NX'

JETSON_MODELS = [JETSON_TX1, JETSON_TX2, CLARA_AGX_XAVIER, JETSON_TX2_NX, JETSON_XAVIER, JETSON_NANO, JETSON_NX, JETSON_ORIN, JETSON_ORIN_NX]

# These arrays contain tuples of all the relevant GPIO data for each Jetson
# Platform. The fields are:
# - Linux GPIO pin number (within chip, not global),
#   (map from chip GPIO count to value, to cater for different numbering schemes)
# - Linux exported GPIO name,
#   (map from chip GPIO count to value, to cater for different naming schemes)
#   (entries omitted if exported filename is gpio%i)
# - GPIO chip sysfs directory
# - Pin number (BOARD mode)
# - Pin number (BCM mode)
# - Pin name (CVM mode)
# - Pin name (TEGRA_SOC mode)
# - PWM chip sysfs directory
# - PWM ID within PWM chip
# The values are used to generate dictionaries that map the corresponding pin
# mode numbers to the Linux GPIO pin number and GPIO chip directory

JETSON_ORIN_NX_PIN_DEFS = [
    ({164: 144}, {164:  'PAC.06'}, "2200000.gpio", 7, 4, 'GPIO09', 'GP167', None, None),
    ({164: 112}, {164:  'PR.04'}, "2200000.gpio", 11, 17, 'UART1_RTS', 'GP72_UART1_RTS_N', None, None),
    ({164:  50}, {164:  'PH.07'}, "2200000.gpio", 12, 18, 'I2S0_SCLK', 'GP122', None, None),
    ({164:  122}, {164:  'PY.00'}, "2200000.gpio", 13, 27, 'SPI1_SCK', 'GP36_SPI3_CLK', None, None),
    ({164:  85}, {164:  'PN.01'}, "2200000.gpio", 15, 22, 'GPIO12', 'GP88_PWM1', '3280000.pwm', 0),
    ({164:   126}, { 164: 'PY.04'}, "2200000.gpio", 16, 23, 'SPI1_CS1', 'GP40_SPI3_CS1_N', None, None),
    ({164:  125}, {164:  'PY.03'}, "2200000.gpio", 18, 24, 'SPI1_CS0', 'GP39_SPI3_CS0_N', None, None),
    ({164: 135}, {164:  'PZ.05'}, "2200000.gpio", 19, 10, 'SPI0_MOSI', 'GP49_SPI1_MOSI', None, None),
    ({164: 134}, {164:  'PZ.04'}, "2200000.gpio", 21, 9, 'SPI0_MISO', 'GP48_SPI1_MISO', None, None),
    ({164: 123}, {164:  'PY.01'}, "2200000.gpio", 22, 25, 'SPI1_MISO', 'GP37_SPI3_MISO', None, None),
    ({164: 133}, {164:  'PZ.03'}, "2200000.gpio", 23, 11, 'SPI0_SCK', 'GP47_SPI1_CLK', None, None),
    ({164: 136}, {164:  'PZ.06'}, "2200000.gpio", 24, 8, 'SPI0_CS0', 'GP50_SPI1_CS0_N', None, None),
    ({164: 137}, {164:  'PZ.07'}, "2200000.gpio", 26, 7, 'SPI0_CS1', 'GP51_SPI1_CS1_N', None, None),
    ({ 164:   105}, { 164: 'PQ.05'}, "2200000.gpio", 29, 5, 'GPIO01', 'GP65', None, None),
    ({ 164:   106}, { 164: 'PQ.06'}, "2200000.gpio", 31, 6, 'GPIO11', 'GP66', None, None),
    ({ 164:  41}, { 164: 'PG.06'}, "2200000.gpio", 32, 12, 'GPIO07', 'GP113_PWM7', None, None),
    ({164:  43}, {164:  'PH.00'}, "2200000.gpio", 33, 13, 'GPIO13', 'GP115', '32c0000.pwm', 0),
    ({164: 53}, {164:  'PI.02'}, "2200000.gpio", 35, 19, 'I2S0_FS', 'GP125', None, None),
    ({164: 113}, {164:  'PR.05'}, "2200000.gpio", 36, 16, 'UART1_CTS', 'GP73_UART1_CTS_N', None, None),
    ({ 164:   124}, { 164: 'PY.02'}, "2200000.gpio", 37, 26, 'SPI1_MOSI', 'GP38_SPI3_MOSI', None, None),
    ({164:  52}, {164:  'PI.01'}, "2200000.gpio", 38, 20, 'I2S0_SDIN', 'GP124', None, None),
    ({164:  51}, {164:  'PI.00'}, "2200000.gpio", 40, 21, 'I2S0_SDOUT', 'GP123', None, None)
]

compats_jetson_orins_nx = (
    "nvidia,p3509-0000+p3767-0000",
    "nvidia,p3768-0000+p3767-0000"
)

JETSON_ORIN_PIN_DEFS = [
    ({164: 106}, {164:  'PQ.06'}, "2200000.gpio", 7, 4, 'MCLK05', 'GP66', None, None),
    # Output-only (due to base board)
    ({164: 112}, {164:  'PR.04'}, "2200000.gpio", 11, 17, 'UART1_RTS', 'GP72_UART1_RTS_N', None, None),
    ({164:  50}, {164:  'PH.07'}, "2200000.gpio", 12, 18, 'I2S2_CLK', 'GP122', None, None),
    ({164:  108}, {164:  'PR.00'}, "2200000.gpio", 13, 27, 'PWM01', 'GP68', None, None),
    ({164:  85}, {164:  'PN.01'}, "2200000.gpio", 15, 22, 'GPIO27', 'GP88_PWM1', '3280000.pwm', 0),
    ({32:   9}, { 32: 'PBB.01'}, "c2f0000.gpio", 16, 23, 'GPIO08', 'GP26', None, None),
    ({164:  43}, {164:  'PH.00'}, "2200000.gpio", 18, 24, 'GPIO35', 'GP115', '32c0000.pwm', 0),
    ({164: 135}, {164:  'PZ.05'}, "2200000.gpio", 19, 10, 'SPI1_MOSI', 'GP49_SPI1_MOSI', None, None),
    ({164: 134}, {164:  'PZ.04'}, "2200000.gpio", 21, 9, 'SPI1_MISO', 'GP48_SPI1_MISO', None, None),
    ({164: 96}, {164:  'PP.04'}, "2200000.gpio", 22, 25, 'GPIO17', 'GP56', None, None),
    ({164: 133}, {164:  'PZ.03'}, "2200000.gpio", 23, 11, 'SPI1_CLK', 'GP47_SPI1_CLK', None, None),
    ({164: 136}, {164:  'PZ.06'}, "2200000.gpio", 24, 8, 'SPI1_CS0_N', 'GP50_SPI1_CS0_N', None, None),
    ({164: 137}, {164:  'PZ.07'}, "2200000.gpio", 26, 7, 'SPI1_CS1_N', 'GP51_SPI1_CS1_N', None, None),
    ({ 32:   1}, { 32: 'PAA.01'}, "c2f0000.gpio", 29, 5, 'CAN0_DIN', 'GP18_CAN0_DIN', None, None),
    ({ 32:   0}, { 32: 'PAA.00'}, "c2f0000.gpio", 31, 6, 'CAN0_DOUT', 'GP17_CAN0_DOUT', None, None),
    ({ 32:  8}, { 32: 'PBB.00'}, "c2f0000.gpio", 32, 12, 'GPIO09', 'GP25', None, None),
    ({ 32:   2}, { 32: 'PAA.02'}, "c2f0000.gpio", 33, 13, 'CAN1_DOUT', 'GP19_CAN1_DOUT', None, None),
    ({164: 53}, {164:  'PI.02'}, "2200000.gpio", 35, 19, 'I2S2_FS', 'GP125', None, None),
    ({164: 113}, {164:  'PR.05'}, "2200000.gpio", 36, 16, 'UART1_CTS', 'GP73_UART1_CTS_N', None, None),
    ({ 32:   3}, { 32: 'PAA.03'}, "c2f0000.gpio", 37, 26, 'CAN1_DIN', 'GP20_CAN1_DIN', None, None),
    ({164:  52}, {164:  'PI.01'}, "2200000.gpio", 38, 20, 'I2S2_DIN', 'GP124', None, None),
    ({164:  51}, {164:  'PI.00'}, "2200000.gpio", 40, 21, 'I2S2_DOUT', 'GP123', None, None)
]

compats_jetson_orins = (
    'nvidia,p3737-0000+p3701-0000',
    'nvidia,p3737-0000+p3701-0004',
)

CLARA_AGX_XAVIER_PIN_DEFS = [
    ({224: 134, 169: 106}, {169:  'PQ.06'}, "2200000.gpio", 7, 4, 'MCLK05', 'SOC_GPIO42', None, None),
    ({224: 140, 169: 112}, {169:  'PR.04'}, "2200000.gpio", 11, 17, 'UART1_RTS', 'UART1_RTS', None, None),
    ({224:  63, 169:  51}, {169:  'PH.07'}, "2200000.gpio", 12, 18, 'I2S2_CLK', 'DAP2_SCLK', None, None),
    ({224: 124, 169:  96}, {169:  'PP.04'}, "2200000.gpio", 13, 27, 'GPIO32', 'SOC_GPIO04', None, None),
    # Older versions of L4T don't enable this PWM controller in DT, so this PWM
    # channel may not be available.[B
    ({224: 105, 169:  84}, {169:  'PN.01'}, "2200000.gpio", 15, 22, 'GPIO27', 'SOC_GPIO54', '3280000.pwm', 0),
    ({ 40:   8,  30:   8}, { 30: 'PBB.00'}, "c2f0000.gpio", 16, 23, 'GPIO8', 'CAN1_STB', None, None),
    ({224:  56, 169:  44}, {169:  'PH.00'}, "2200000.gpio", 18, 24, 'GPIO35', 'SOC_GPIO12', '32c0000.pwm', 0),
    ({224: 205, 169: 162}, {169:  'PZ.05'}, "2200000.gpio", 19, 10, 'SPI1_MOSI', 'SPI1_MOSI', None, None),
    ({224: 204, 169: 161}, {169:  'PZ.04'}, "2200000.gpio", 21, 9, 'SPI1_MISO', 'SPI1_MISO', None, None),
    ({224: 129, 169: 101}, {169:  'PQ.01'}, "2200000.gpio", 22, 25, 'GPIO17', 'SOC_GPIO21', None, None),
    ({224: 203, 169: 160}, {169:  'PZ.03'}, "2200000.gpio", 23, 11, 'SPI1_CLK', 'SPI1_SCK', None, None),
    ({224: 206, 169: 163}, {169:  'PZ.06'}, "2200000.gpio", 24, 8, 'SPI1_CS0_N', 'SPI1_CS0_N', None, None),
    ({224: 207, 169: 164}, {169:  'PZ.07'}, "2200000.gpio", 26, 7, 'SPI1_CS1_N', 'SPI1_CS1_N', None, None),
    ({ 40:   3,  30:   3}, { 30: 'PAA.03'}, "c2f0000.gpio", 29, 5, 'CAN0_DIN', 'CAN0_DIN', None, None),
    ({ 40:   2,  30:   2}, { 30: 'PAA.02'}, "c2f0000.gpio", 31, 6, 'CAN0_DOUT', 'CAN0_DOUT', None, None),
    ({ 40:   9,  30:   9}, { 30: 'PBB.01'}, "c2f0000.gpio", 32, 12, 'GPIO9', 'CAN1_EN', None, None),
    ({ 40:   0,  30:   0}, { 30: 'PAA.00'}, "c2f0000.gpio", 33, 13, 'CAN1_DOUT', 'CAN1_DOUT', None, None),
    ({224:  66, 169:  54}, {169:  'PI.02'}, "2200000.gpio", 35, 19, 'I2S2_FS', 'DAP2_FS', None, None),
    # Input-only (due to base board)
    ({224: 141, 169: 113}, {169:  'PR.05'}, "2200000.gpio", 36, 16, 'UART1_CTS', 'UART1_CTS', None, None),
    ({ 40:   1,  30:   1}, { 30: 'PAA.01'}, "c2f0000.gpio", 37, 26, 'CAN1_DIN', 'CAN1_DIN', None, None),
    ({224:  65, 169:  53}, {169:  'PI.01'}, "2200000.gpio", 38, 20, 'I2S2_DIN', 'DAP2_DIN', None, None),
    ({224:  64, 169:  52}, {169:  'PI.00'}, "2200000.gpio", 40, 21, 'I2S2_DOUT', 'DAP2_DOUT', None, None)
]
compats_clara_agx_xavier = (
    'nvidia,e3900-0000+p2888-0004',
)

JETSON_NX_PIN_DEFS = [
    ({224: 148, 169: 118}, {169:  'PS.04'}, "2200000.gpio", 7, 4, 'GPIO09', 'AUD_MCLK', None, None),
    ({224: 140, 169: 112}, {169:  'PR.04'}, "2200000.gpio", 11, 17, 'UART1_RTS', 'UART1_RTS', None, None),
    ({224: 157, 169: 127}, {169:  'PT.05'}, "2200000.gpio", 12, 18, 'I2S0_SCLK', 'DAP5_SCLK', None, None),
    ({224: 192, 169: 149}, {169:  'PY.00'}, "2200000.gpio", 13, 27, 'SPI1_SCK', 'SPI3_SCK', None, None),
    ({ 40:  20,  30:  16}, { 30: 'PCC.04'}, "c2f0000.gpio", 15, 22, 'GPIO12', 'TOUCH_CLK', "c340000.pwm", 0),
    ({224: 196, 169: 153}, {169:  'PY.04'}, "2200000.gpio", 16, 23, 'SPI1_CS1', 'SPI3_CS1_N', None, None),
    ({224: 195, 169: 152}, {169:  'PY.03'}, "2200000.gpio", 18, 24, 'SPI1_CS0', 'SPI3_CS0_N', None, None),
    ({224: 205, 169: 162}, {169:  'PZ.05'}, "2200000.gpio", 19, 10, 'SPI0_MOSI', 'SPI1_MOSI', None, None),
    ({224: 204, 169: 161}, {169:  'PZ.04'}, "2200000.gpio", 21, 9, 'SPI0_MISO', 'SPI1_MISO', None, None),
    ({224: 193, 169: 150}, {169:  'PY.01'}, "2200000.gpio", 22, 25, 'SPI1_MISO', 'SPI3_MISO', None, None),
    ({224: 203, 169: 160}, {169:  'PZ.03'}, "2200000.gpio", 23, 11, 'SPI0_SCK', 'SPI1_SCK', None, None),
    ({224: 206, 169: 163}, {169:  'PZ.06'}, "2200000.gpio", 24, 8, 'SPI0_CS0', 'SPI1_CS0_N', None, None),
    ({224: 207, 169: 164}, {169:  'PZ.07'}, "2200000.gpio", 26, 7, 'SPI0_CS1', 'SPI1_CS1_N', None, None),
    ({224: 133, 169: 105}, {169:  'PQ.05'}, "2200000.gpio", 29, 5, 'GPIO01', 'SOC_GPIO41', None, None),
    ({224: 134, 169: 106}, {169:  'PQ.06'}, "2200000.gpio", 31, 6, 'GPIO11', 'SOC_GPIO42', None, None),
    ({224: 136, 169: 108}, {169:  'PR.00'}, "2200000.gpio", 32, 12, 'GPIO07', 'SOC_GPIO44', '32f0000.pwm', 0),
    ({224: 105, 169:  84}, {169:  'PN.01'}, "2200000.gpio", 33, 13, 'GPIO13', 'SOC_GPIO54', '3280000.pwm', 0),
    ({224: 160, 169: 130}, {169:  'PU.00'}, "2200000.gpio", 35, 19, 'I2S0_FS', 'DAP5_FS', None, None),
    ({224: 141, 169: 113}, {169:  'PR.05'}, "2200000.gpio", 36, 16, 'UART1_CTS', 'UART1_CTS', None, None),
    ({224: 194, 169: 151}, {169:  'PY.02'}, "2200000.gpio", 37, 26, 'SPI1_MOSI', 'SPI3_MOSI', None, None),
    ({224: 159, 169: 129}, {169:  'PT.07'}, "2200000.gpio", 38, 20, 'I2S0_DIN', 'DAP5_DIN', None, None),
    ({224: 158, 169: 128}, {169:  'PT.06'}, "2200000.gpio", 40, 21, 'I2S0_DOUT', 'DAP5_DOUT', None, None)
]
compats_nx = (
    'nvidia,p3509-0000+p3668-0000',
    'nvidia,p3509-0000+p3668-0001',
    'nvidia,p3449-0000+p3668-0000',
    'nvidia,p3449-0000+p3668-0001',
    'nvidia,p3449-0000+p3668-0003',
)

JETSON_XAVIER_PIN_DEFS = [
    ({224: 134, 169: 106}, {169:  'PQ.06'}, "2200000.gpio", 7, 4, 'MCLK05', 'SOC_GPIO42', None, None),
    ({224: 140, 169: 112}, {169:  'PR.04'}, "2200000.gpio", 11, 17, 'UART1_RTS', 'UART1_RTS', None, None),
    ({224:  63, 169:  51}, {169:  'PH.07'}, "2200000.gpio", 12, 18, 'I2S2_CLK', 'DAP2_SCLK', None, None),
    ({224: 136, 169: 108}, {169:  'PR.00'}, "2200000.gpio", 13, 27, 'PWM01', 'SOC_GPIO44', '32f0000.pwm', 0),
    # Older versions of L4T don'Pt enable this PWM controller in DT, so this PWM
    # channel may not be available.
    ({224: 105, 169:  84}, {169:  'PN.01'}, "2200000.gpio", 15, 22, 'GPIO27', 'SOC_GPIO54', '3280000.pwm', 0),
    ({ 40:   8,  30:   8}, { 30: 'PBB.00'}, "c2f0000.gpio", 16, 23, 'GPIO8', 'CAN1_STB', None, None),
    ({224:  56, 169:  44}, {169:  'PH.00'}, "2200000.gpio", 18, 24, 'GPIO35', 'SOC_GPIO12', '32c0000.pwm', 0),
    ({224: 205, 169: 162}, {169:  'PZ.05'}, "2200000.gpio", 19, 10, 'SPI1_MOSI', 'SPI1_MOSI', None, None),
    ({224: 204, 169: 161}, {169:  'PZ.04'}, "2200000.gpio", 21, 9, 'SPI1_MISO', 'SPI1_MISO', None, None),
    ({224: 129, 169: 101}, {169:  'PQ.01'}, "2200000.gpio", 22, 25, 'GPIO17', 'SOC_GPIO21', None, None),
    ({224: 203, 169: 160}, {169:  'PZ.03'}, "2200000.gpio", 23, 11, 'SPI1_CLK', 'SPI1_SCK', None, None),
    ({224: 206, 169: 163}, {169:  'PZ.06'}, "2200000.gpio", 24, 8, 'SPI1_CS0_N', 'SPI1_CS0_N', None, None),
    ({224: 207, 169: 164}, {169:  'PZ.07'}, "2200000.gpio", 26, 7, 'SPI1_CS1_N', 'SPI1_CS1_N', None, None),
    ({ 40:   3,  30:   3}, { 30: 'PAA.03'}, "c2f0000.gpio", 29, 5, 'CAN0_DIN', 'CAN0_DIN', None, None),
    ({ 40:   2,  30:   2}, { 30: 'PAA.02'}, "c2f0000.gpio", 31, 6, 'CAN0_DOUT', 'CAN0_DOUT', None, None),
    ({ 40:   9,  30:   9}, { 30: 'PBB.01'}, "c2f0000.gpio", 32, 12, 'GPIO9', 'CAN1_EN', None, None),
    ({ 40:   0,  30:   0}, { 30: 'PAA.00'}, "c2f0000.gpio", 33, 13, 'CAN1_DOUT', 'CAN1_DOUT', None, None),
    ({224:  66, 169:  54}, {169:  'PI.02'}, "2200000.gpio", 35, 19, 'I2S2_FS', 'DAP2_FS', None, None),
    # Input-only (due to base board)
    ({224: 141, 169: 113}, {169:  'PR.05'}, "2200000.gpio", 36, 16, 'UART1_CTS', 'UART1_CTS', None, None),
    ({ 40:   1,  30:   1}, { 30: 'PAA.01'}, "c2f0000.gpio", 37, 26, 'CAN1_DIN', 'CAN1_DIN', None, None),
    ({224:  65, 169:  53}, {169:  'PI.01'}, "2200000.gpio", 38, 20, 'I2S2_DIN', 'DAP2_DIN', None, None),
    ({224:  64, 169:  52}, {169:  'PI.00'}, "2200000.gpio", 40, 21, 'I2S2_DOUT', 'DAP2_DOUT', None, None)
]
compats_xavier = (
    'nvidia,p2972-0000',
    'nvidia,p2972-0006',
    'nvidia,jetson-xavier',
    'nvidia,galen-industrial',
    'nvidia,jetson-xavier-industrial',
)

JETSON_TX2_NX_PIN_DEFS = [
    ({192:  76, 140: 66}, {140:  'PJ.04'}, "2200000.gpio", 7, 4, 'GPIO09', 'AUD_MCLK', None, None),
    ({64: 28, 47: 23}, {47:  'PW.04'}, "c2f0000.gpio", 11, 17, 'UART1_RTS', 'UART3_RTS', None, None),
    ({192:  72, 140: 62}, {140:  'PJ.00'}, "2200000.gpio", 12, 18, 'I2S0_SCLK', 'DAP1_SCLK', None, None),
    ({64:  17, 47: 12}, {47:  'PV.01'}, "c2f0000.gpio", 13, 27, 'SPI1_SCK', 'GPIO_SEN1', None, None),
    ({192:  18,  140: 16}, {140: 'PC.02'}, "2200000.gpio", 15, 22, 'GPIO12', 'DAP2_DOUT', None, None),
    ({192: 19, 140: 17}, {140:  'PC.03'}, "2200000.gpio", 16, 23, 'SPI1_CS1', 'DAP2_DIN', None, None),
    ({64: 20, 47: 15}, {47:  'PV.04'}, "c2f0000.gpio", 18, 24, 'SPI1_CS0', 'GPIO_SEN4', None, None),
    ({192: 58, 140:  49}, {140:  'PH.02'}, "2200000.gpio", 19, 10, 'SPI0_MOSI', 'GPIO_WAN7', None, None),
    ({192: 57, 140: 48}, {140:  'PH.01'}, "2200000.gpio", 21, 9, 'SPI0_MISO', 'GPIO_WAN6', None, None),
    ({64: 18, 47: 13}, {47:  'PV.02'}, "c2f0000.gpio", 22, 25, 'SPI1_MISO', 'GPIO_SEN2', None, None),
    ({192: 56, 140:  47}, {140:  'PH.00'}, "2200000.gpio", 23, 11, 'SPI1_CLK', 'GPIO_WAN5', None, None),
    ({192: 59, 140: 50}, {140:  'PH.03'}, "2200000.gpio", 24, 8, 'SPI0_CS0', 'GPIO_WAN8', None, None),
    ({192: 163, 140: 130}, {140:  'PY.03'}, "2200000.gpio", 26, 7, 'SPI0_CS1', 'GPIO_MDM4', None, None),
    ({192: 105, 140: 86}, {140:  'PN.01'}, "2200000.gpio", 29, 5, 'GPIO01', 'GPIO_CAM2', None, None),
    ({64: 50, 47: 41}, {47:  'PEE.02'}, "c2f0000.gpio", 31, 6, 'GPIO11', 'TOUCH_CLK', None, None),
    ({64: 8, 47: 5}, {47:  'PU.00'}, "c2f0000.gpio", 32, 12, 'GPIO07', 'GPIO_DIS0', '3280000.pwm', 0),
    ({64: 13, 47: 10}, {47:  'PU.05'}, "c2f0000.gpio", 33, 13, 'GPIO13', 'GPIO_DIS5', '32a0000.pwm', 0),
    ({192: 75, 140: 65}, {140:  'PJ.03'}, "2200000.gpio", 35, 19, 'I2S0_FS', 'DAP1_FS', None, None),
    ({64: 29, 47: 24}, {47:  'PW.05'}, "c2f0000.gpio", 36, 16, 'UART1_CTS', 'UART3_CTS', None, None),
    ({64: 19, 47: 14}, {47:  'PV.03'}, "c2f0000.gpio", 37, 26, 'SPI1_MOSI', 'GPIO_SEN3', None, None),
    ({192: 74, 140: 64}, {140:  'PJ.02'}, "2200000.gpio", 38, 20, 'I2S0_DIN', 'DAP1_DIN', None, None),
    ({192:  73, 140:  63}, {140:  'PJ.01'}, "2200000.gpio", 40, 21, 'I2S0_DOUT', 'DAP1_DOUT', None, None)
]
compats_tx2_nx = (
    'nvidia,p3509-0000+p3636-0001',
)

JETSON_TX2_PIN_DEFS = [
    ({192:  76, 140:  66}, {140:  'PJ.04'}, "2200000.gpio", 7, 4, 'PAUDIO_MCLK', 'AUD_MCLK', None, None),
    # Output-only (due to base board)
    ({192: 146, 140: 117}, {140:  'PT.02'}, "2200000.gpio", 11, 17, 'PUART0_RTS', 'UART1_RTS', None, None),
    ({192:  72, 140:  62}, {140:  'PJ.00'}, "2200000.gpio", 12, 18, 'PI2S0_CLK', 'DAP1_SCLK', None, None),
    ({192:  77, 140:  67}, {140:  'PJ.05'}, "2200000.gpio", 13, 27, 'PGPIO20_AUD_INT', 'GPIO_AUD0', None, None),
    (                  15,              {}, "3160000.i2c/i2c-0/0-0074", 15, 22, 'GPIO_EXP_P17', 'GPIO_EXP_P17', None, None),
    # Input-only (due to module):
    ({ 64:  40,  47:  31}, { 47: 'PAA.00'}, "c2f0000.gpio", 16, 23, 'AO_DMIC_IN_DAT', 'CAN_GPIO0', None, None),
    ({192: 161, 140: 128}, {140:  'PY.01'}, "2200000.gpio", 18, 24, 'GPIO16_MDM_WAKE_AP', 'GPIO_MDM2', None, None),
    ({192: 109, 140:  90}, {140:  'PN.05'}, "2200000.gpio", 19, 10, 'SPI1_MOSI', 'GPIO_CAM6', None, None),
    ({192: 108, 140:  89}, {140:  'PN.04'}, "2200000.gpio", 21, 9, 'SPI1_MISO', 'GPIO_CAM5', None, None),
    (                  14,              {}, "3160000.i2c/i2c-0/0-0074", 22, 25, 'GPIO_EXP_P16', 'GPIO_EXP_P16', None, None),
    ({192: 107, 140:  88}, {140:  'PN.03'}, "2200000.gpio", 23, 11, 'SPI1_CLK', 'GPIO_CAM4', None, None),
    ({192: 110, 140:  91}, {140:  'PN.06'}, "2200000.gpio", 24, 8, 'SPI1_CS0', 'GPIO_CAM7', None, None),
    # Board pin 26 is not available on this board
    ({192:  78, 140:  68}, {140:  'PJ.06'}, "2200000.gpio", 29, 5, 'GPIO19_AUD_RST', 'GPIO_AUD1', None, None),
    ({ 64:  42,  47:  33}, { 47: 'PAA.02'}, "c2f0000.gpio", 31, 6, 'GPIO9_MOTION_INT', 'CAN_GPIO2', None, None),
    # Output-only (due to module):
    ({ 64:  41,  47:  32}, { 47: 'PAA.01'}, "c2f0000.gpio", 32, 12, 'AO_DMIC_IN_CLK', 'CAN_GPIO1', None, None),
    ({192:  69, 140:  59}, {140:  'PI.05'}, "2200000.gpio", 33, 13, 'GPIO11_AP_WAKE_BT', 'GPIO_PQ5', None, None),
    ({192:  75, 140:  65}, {140:  'PJ.03'}, "2200000.gpio", 35, 19, 'I2S0_LRCLK', 'DAP1_FS', None, None),
    # Input-only (due to base board) IF NVIDIA debug card NOT plugged in
    # Output-only (due to base board) IF NVIDIA debug card plugged in
    ({192: 147, 140: 118}, {140:  'PT.03'}, "2200000.gpio", 36, 16, 'UART0_CTS', 'UART1_CTS', None, None),
    ({192:  68, 140:  58}, {140:  'PI.04'}, "2200000.gpio", 37, 26, 'GPIO8_ALS_PROX_INT', 'GPIO_PQ4', None, None),
    ({192:  74, 140:  64}, {140:  'PJ.02'}, "2200000.gpio", 38, 20, 'I2S0_SDIN', 'DAP1_DIN', None, None),
    ({192:  73, 140:  63}, {140:  'PJ.01'}, "2200000.gpio", 40, 21, 'I2S0_SDOUT', 'DAP1_DOUT', None, None)
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
    (216, {}, "6000d000.gpio", 7, 4, 'AUDIO_MCLK', 'AUD_MCLK', None, None),
    # Output-only (due to base board)
    (162, {}, "6000d000.gpio", 11, 17, 'UART0_RTS', 'UART1_RTS', None, None),
    (11, {}, "6000d000.gpio", 12, 18, 'I2S0_CLK', 'DAP1_SCLK', None, None),
    (38, {}, "6000d000.gpio", 13, 27, 'GPIO20_AUD_INT', 'GPIO_PE6', None, None),
    (15, {}, "7000c400.i2c/i2c-1/1-0074", 15, 22, 'GPIO_EXP_P17', 'GPIO_EXP_P17', None, None),
    (37, {}, "6000d000.gpio", 16, 23, 'AO_DMIC_IN_DAT', 'DMIC3_DAT', None, None),
    (184, {}, "6000d000.gpio", 18, 24, 'GPIO16_MDM_WAKE_AP', 'MODEM_WAKE_AP', None, None),
    (16, {}, "6000d000.gpio", 19, 10, 'SPI1_MOSI', 'SPI1_MOSI', None, None),
    (17, {}, "6000d000.gpio", 21, 9, 'SPI1_MISO', 'SPI1_MISO', None, None),
    (14, {}, "7000c400.i2c/i2c-1/1-0074", 22, 25, 'GPIO_EXP_P16', 'GPIO_EXP_P16', None, None),
    (18, {}, "6000d000.gpio", 23, 11, 'SPI1_CLK', 'SPI1_SCK', None, None),
    (19, {}, "6000d000.gpio", 24, 8, 'SPI1_CS0', 'SPI1_CS0', None, None),
    (20, {}, "6000d000.gpio", 26, 7, 'SPI1_CS1', 'SPI1_CS1', None, None),
    (219, {}, "6000d000.gpio", 29, 5, 'GPIO19_AUD_RST', 'GPIO_X1_AUD', None, None),
    (186, {}, "6000d000.gpio", 31, 6, 'GPIO9_MOTION_INT', 'MOTION_INT', None, None),
    (36, {}, "6000d000.gpio", 32, 12, 'AO_DMIC_IN_CLK', 'DMIC3_CLK', None, None),
    (63, {}, "6000d000.gpio", 33, 13, 'GPIO11_AP_WAKE_BT', 'AP_WAKE_NFC', None, None),
    (8, {}, "6000d000.gpio", 35, 19, 'I2S0_LRCLK', 'DAP1_FS', None, None),
    # Input-only (due to base board) IF NVIDIA debug card NOT plugged in
    # Input-only (due to base board) (always reads fixed value) IF NVIDIA debug card plugged in
    (163, {}, "6000d000.gpio", 36, 16, 'UART0_CTS', 'UART1_CTS', None, None),
    (187, {}, "6000d000.gpio", 37, 26, 'GPIO8_ALS_PROX_INT', 'ALS_PROX_INT', None, None),
    (9, {}, "6000d000.gpio", 38, 20, 'I2S0_SDIN', 'DAP1_DIN', None, None),
    (10, {}, "6000d000.gpio", 40, 21, 'I2S0_SDOUT', 'DAP1_DOUT', None, None)
]
compats_tx1 = (
    'nvidia,p2371-2180',
    'nvidia,jetson-cv',
)

JETSON_NANO_PIN_DEFS = [
    (216, {}, "6000d000.gpio", 7, 4, 'GPIO9', 'AUD_MCLK', None, None),
    (50, {}, "6000d000.gpio", 11, 17, 'UART1_RTS', 'UART2_RTS', None, None),
    (79, {}, "6000d000.gpio", 12, 18, 'I2S0_SCLK', 'DAP4_SCLK', None, None),
    (14, {}, "6000d000.gpio", 13, 27, 'SPI1_SCK', 'SPI2_SCK', None, None),
    (194, {}, "6000d000.gpio", 15, 22, 'GPIO12', 'LCD_TE', None, None),
    (232, {}, "6000d000.gpio", 16, 23, 'SPI1_CS1', 'SPI2_CS1', None, None),
    (15, {}, "6000d000.gpio", 18, 24, 'SPI1_CS0', 'SPI2_CS0', None, None),
    (16, {}, "6000d000.gpio", 19, 10, 'SPI0_MOSI', 'SPI1_MOSI', None, None),
    (17, {}, "6000d000.gpio", 21, 9, 'SPI0_MISO', 'SPI1_MISO', None, None),
    (13, {}, "6000d000.gpio", 22, 25, 'SPI1_MISO', 'SPI2_MISO', None, None),
    (18, {}, "6000d000.gpio", 23, 11, 'SPI0_SCK', 'SPI1_SCK', None, None),
    (19, {}, "6000d000.gpio", 24, 8, 'SPI0_CS0', 'SPI1_CS0', None, None),
    (20, {}, "6000d000.gpio", 26, 7, 'SPI0_CS1', 'SPI1_CS1', None, None),
    (149, {}, "6000d000.gpio", 29, 5, 'GPIO01', 'CAM_AF_EN', None, None),
    (200, {}, "6000d000.gpio", 31, 6, 'GPIO11', 'GPIO_PZ0', None, None),
    # Older versions of L4T have a DT bug which instantiates a bogus device
    # which prevents this library from using this PWM channel.
    (168, {}, "6000d000.gpio", 32, 12, 'GPIO07', 'LCD_BL_PW', '7000a000.pwm', 0),
    (38, {}, "6000d000.gpio", 33, 13, 'GPIO13', 'GPIO_PE6', '7000a000.pwm', 2),
    (76, {}, "6000d000.gpio", 35, 19, 'I2S0_FS', 'DAP4_FS', None, None),
    (51, {}, "6000d000.gpio", 36, 16, 'UART1_CTS', 'UART2_CTS', None, None),
    (12, {}, "6000d000.gpio", 37, 26, 'SPI1_MOSI', 'SPI2_MOSI', None, None),
    (77, {}, "6000d000.gpio", 38, 20, 'I2S0_DIN', 'DAP4_DIN', None, None),
    (78, {}, "6000d000.gpio", 40, 21, 'I2S0_DOUT', 'DAP4_DOUT', None, None)
]
compats_nano = (
    'nvidia,p3450-0000',
    'nvidia,p3450-0002',
    'nvidia,jetson-nano',
)

jetson_gpio_data = {
    JETSON_ORIN_NX: (
        JETSON_ORIN_NX_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '32768M, 65536M',
            'REVISION': 'Unknown',
            'TYPE': 'JETSON_ORIN_NX',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'A78AE'
        }
    ),
    JETSON_ORIN: (
        JETSON_ORIN_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '32768M, 65536M',
            'REVISION': 'Unknown',
            'TYPE': 'JETSON_ORIN',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'A78AE'
        }
    ),
    CLARA_AGX_XAVIER: (
        CLARA_AGX_XAVIER_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '16384M',
            'REVISION': 'Unknown',
            'TYPE': 'CLARA_AGX_XAVIER',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'ARM Carmel'
        }
    ),
    JETSON_NX: (
        JETSON_NX_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '16384M, 8192M',
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
            'RAM': '65536M, 32768M, 16384M, 8192M',
            'REVISION': 'Unknown',
            'TYPE': 'Jetson Xavier',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'ARM Carmel'
        }
    ),
    JETSON_TX2_NX: (
        JETSON_TX2_NX_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '4096M',
            'REVISION': 'Unknown',
            'TYPE': 'Jetson TX2 NX',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'ARM A57 + Denver'
        }
    ),
    JETSON_TX2: (
        JETSON_TX2_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '8192M, 4096M',
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
            'RAM': '4096M, 2048M',
            'REVISION': 'Unknown',
            'TYPE': 'Jetson Nano',
            'MANUFACTURER': 'NVIDIA',
            'PROCESSOR': 'ARM A57'
        }
    ),
}


class ChannelInfo(object):
    def __init__(self, channel, gpio_chip_dir, chip_gpio, gpio, gpio_name, pwm_chip_dir, pwm_id):
        self.channel = channel
        self.gpio_chip_dir = gpio_chip_dir
        self.chip_gpio = chip_gpio
        self.gpio = gpio
        self.gpio_name = gpio_name
        self.pwm_chip_dir = pwm_chip_dir
        self.pwm_id = pwm_id


ids_warned = False

def find_pmgr_board(prefix):
    global ids_warned
    ids_path = '/proc/device-tree/chosen/plugin-manager/ids'
    ids_path_k510 = '/proc/device-tree/chosen/ids'

    if os.path.exists(ids_path):
        for f in os.listdir(ids_path):
            if f.startswith(prefix):
                return f
    elif os.path.exists(ids_path_k510):
        with open(ids_path_k510, 'r') as f:
            ids = f.read()
            for s in ids.split():
                if s.startswith(prefix):
                    return s
    else:
        if not ids_warned:
            ids_warned = True
            msg = """\
WARNING: Plugin manager information missing from device tree.
WARNING: Cannot determine whether the expected Jetson board is present.
"""
            sys.stderr.write(msg)

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


def get_compatibles(compatible_path):
    with open(compatible_path, 'r') as f:
        compatibles = f.read().split('\x00')
    return compatibles


def get_model():
    compatible_path = '/proc/device-tree/compatible'

    # get model info from compatible_path
    if os.path.exists(compatible_path):
        compatibles = get_compatibles(compatible_path)

        def matches(vals):
            return any(v in compatibles for v in vals)

        if matches(compats_tx1):
            warn_if_not_carrier_board('2597')
            return JETSON_TX1
        elif matches(compats_tx2):
            warn_if_not_carrier_board('2597')
            return JETSON_TX2
        elif matches(compats_clara_agx_xavier):
            warn_if_not_carrier_board('3900')
            return CLARA_AGX_XAVIER
        elif matches(compats_tx2_nx):
            warn_if_not_carrier_board('3509')
            return JETSON_TX2_NX
        elif matches(compats_xavier):
            warn_if_not_carrier_board('2822')
            return JETSON_XAVIER
        elif matches(compats_nano):
            module_id = find_pmgr_board('3448')
            if not module_id:
                raise Exception('Could not determine Jetson Nano module revision')
            revision = module_id.split('-')[-1]
            # Revision is an ordered string, not a decimal integer
            if revision < "200":
                raise Exception('Jetson Nano module revision must be A02 or later')
            warn_if_not_carrier_board('3449', '3542')
            return JETSON_NANO
        elif matches(compats_nx):
            warn_if_not_carrier_board('3509', '3449')
            return JETSON_NX
        elif matches(compats_jetson_orins):
            warn_if_not_carrier_board('3737')
            return JETSON_ORIN
        elif matches(compats_jetson_orins_nx):
            warn_if_not_carrier_board('3509','3768')
            return JETSON_ORIN_NX

    # get model info from the environment variables for docker containers
    model_name = os.environ.get("JETSON_MODEL_NAME")
    if model_name is not None:
        model_name = model_name.strip()
        if model_name in JETSON_MODELS:
            return model_name
        else:
            msg = f"Environment variable 'JETSON_MODEL_NAME={model_name}' is invalid."
            sys.stderr.write(msg)

    raise Exception('Could not determine Jetson model')


def get_data():
    model = get_model()

    pin_defs, jetson_info = jetson_gpio_data[model]
    gpio_chip_dirs = {}
    gpio_chip_base = {}
    gpio_chip_ngpio = {}
    pwm_dirs = {}

    sysfs_prefixes = ['/sys/devices/', '/sys/devices/platform/']

    # Get the gpiochip offsets
    gpio_chip_names = set([x[2] for x in pin_defs if x[2] is not None])
    for gpio_chip_name in gpio_chip_names:
        gpio_chip_dir = None
        for prefix in sysfs_prefixes:
            d = prefix + gpio_chip_name
            if os.path.isdir(d):
                gpio_chip_dir = d
                break
        if gpio_chip_dir is None:
            raise Exception('Cannot find GPIO chip ' + gpio_chip_name)
        gpio_chip_dirs[gpio_chip_name] = gpio_chip_dir
        gpio_chip_gpio_dir = gpio_chip_dir + '/gpio'
        for fn in os.listdir(gpio_chip_gpio_dir):
            if not fn.startswith('gpiochip'):
                continue
            base_fn = gpio_chip_gpio_dir + '/' + fn + '/base'
            with open(base_fn, 'r') as f:
                gpio_chip_base[gpio_chip_name] = int(f.read().strip())
            ngpio_fn = gpio_chip_gpio_dir + '/' + fn + '/ngpio'
            with open(ngpio_fn, 'r') as f:
                gpio_chip_ngpio[gpio_chip_name] = int(f.read().strip())
            break

    def global_gpio_id_name(chip_relative_ids, gpio_names, gpio_chip_name):
        chip_gpio_ngpio = gpio_chip_ngpio[gpio_chip_name]
        if isinstance(chip_relative_ids, dict):
            chip_relative_id = chip_relative_ids[chip_gpio_ngpio]
        else:
            chip_relative_id = chip_relative_ids
        gpio = gpio_chip_base[gpio_chip_name] + chip_relative_id
        if isinstance(gpio_names, dict):
            gpio_name = gpio_names.get(chip_gpio_ngpio, None)
        else:
            gpio_name = gpio_names
        if gpio_name is None:
            gpio_name = 'gpio%i' % gpio
        return (gpio, gpio_name)

    pwm_chip_names = set([x[7] for x in pin_defs if x[7] is not None])
    for pwm_chip_name in pwm_chip_names:
        pwm_chip_dir = None
        for prefix in sysfs_prefixes:
            d = prefix + pwm_chip_name
            if os.path.isdir(d):
                pwm_chip_dir = d
                break
        # Some PWM controllers aren't enabled in all versions of the DT. In
        # this case, just hide the PWM function on this pin, but let all other
        # aspects of the library continue to work.
        if pwm_chip_dir is None:
            continue
        pwm_chip_pwm_dir = pwm_chip_dir + '/pwm'
        if not os.path.exists(pwm_chip_pwm_dir):
            continue
        for fn in os.listdir(pwm_chip_pwm_dir):
            if not fn.startswith('pwmchip'):
                continue
            pwm_chip_pwm_pwmchipn_dir = pwm_chip_pwm_dir + '/' + fn
            pwm_dirs[pwm_chip_name] = pwm_chip_pwm_pwmchipn_dir
            break

    def model_data(key_col, pin_defs):
        return {x[key_col]: ChannelInfo(
            x[key_col],
            gpio_chip_dirs[x[2]],
            x[0],
            *global_gpio_id_name(*x[0:3]),
            pwm_chip_dir=pwm_dirs.get(x[7], None),
            pwm_id=x[8]) for x in pin_defs}

    channel_data = {
        'BOARD': model_data(3, pin_defs),
        'BCM': model_data(4, pin_defs),
        'CVM': model_data(5, pin_defs),
        'TEGRA_SOC': model_data(6, pin_defs),
    }

    return model, jetson_info, channel_data

