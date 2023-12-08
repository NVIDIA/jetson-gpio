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
JETSON_ORIN_NANO='JETSON_ORIN_NANO'

JETSON_MODELS = [JETSON_TX1, JETSON_TX2, CLARA_AGX_XAVIER, JETSON_TX2_NX, JETSON_XAVIER, JETSON_NANO, JETSON_NX, JETSON_ORIN, JETSON_ORIN_NX, JETSON_ORIN_NANO]

# These arrays contain tuples of all the relevant GPIO data for each Jetson
# Platform. The fields are:
# - Linux GPIO pin number (line offset inside chip, not global),
# - Linux exported GPIO name,
#   (map from chip GPIO count to value, to cater for different naming schemes)
#   (entries omitted if exported filename is gpio%i)
# - GPIO chip name/instance
# - Pin number (BOARD mode)
# - Pin number (BCM mode)
# - Pin name (CVM mode)
# - Pin name (TEGRA_SOC mode)
# - PWM chip sysfs directory
# - PWM ID within PWM chip
# The values are used to generate dictionaries that map the corresponding pin
# mode numbers to the Linux GPIO pin number and GPIO chip directory

JETSON_ORIN_NX_PIN_DEFS = [
    (144, 'PAC.06', "tegra234-gpio", 7, 4, 'GPIO09', 'GP167', None, None),
    (112, 'PR.04', "tegra234-gpio", 11, 17, 'UART1_RTS', 'GP72_UART1_RTS_N', None, None),
    (50, 'PH.07', "tegra234-gpio", 12, 18, 'I2S0_SCLK', 'GP122', None, None),
    (122, 'PY.00', "tegra234-gpio", 13, 27, 'SPI1_SCK', 'GP36_SPI3_CLK', None, None),
    (85, 'PN.01', "tegra234-gpio", 15, 22, 'GPIO12', 'GP88_PWM1', '3280000.pwm', 0),
    (126, 'PY.04', "tegra234-gpio", 16, 23, 'SPI1_CS1', 'GP40_SPI3_CS1_N', None, None),
    (125, 'PY.03', "tegra234-gpio", 18, 24, 'SPI1_CS0', 'GP39_SPI3_CS0_N', None, None),
    (135, 'PZ.05', "tegra234-gpio", 19, 10, 'SPI0_MOSI', 'GP49_SPI1_MOSI', None, None),
    (134, 'PZ.04', "tegra234-gpio", 21, 9, 'SPI0_MISO', 'GP48_SPI1_MISO', None, None),
    (123, 'PY.01', "tegra234-gpio", 22, 25, 'SPI1_MISO', 'GP37_SPI3_MISO', None, None),
    (133, 'PZ.03', "tegra234-gpio", 23, 11, 'SPI0_SCK', 'GP47_SPI1_CLK', None, None),
    (136, 'PZ.06', "tegra234-gpio", 24, 8, 'SPI0_CS0', 'GP50_SPI1_CS0_N', None, None),
    (137, 'PZ.07', "tegra234-gpio", 26, 7, 'SPI0_CS1', 'GP51_SPI1_CS1_N', None, None),
    (105, 'PQ.05', "tegra234-gpio", 29, 5, 'GPIO01', 'GP65', None, None),
    (106, 'PQ.06', "tegra234-gpio", 31, 6, 'GPIO11', 'GP66', None, None),
    (41, 'PG.06', "tegra234-gpio", 32, 12, 'GPIO07', 'GP113_PWM7', '32e0000.pwm', 0),
    (43, 'PH.00', "tegra234-gpio", 33, 13, 'GPIO13', 'GP115', '32c0000.pwm', 0),
    (53, 'PI.02', "tegra234-gpio", 35, 19, 'I2S0_FS', 'GP125', None, None),
    (113, 'PR.05', "tegra234-gpio", 36, 16, 'UART1_CTS', 'GP73_UART1_CTS_N', None, None),
    (124, 'PY.02', "tegra234-gpio", 37, 26, 'SPI1_MOSI', 'GP38_SPI3_MOSI', None, None),
    (52, 'PI.01', "tegra234-gpio", 38, 20, 'I2S0_SDIN', 'GP124', None, None),
    (51, 'PI.00', "tegra234-gpio", 40, 21, 'I2S0_SDOUT', 'GP123', None, None)
]

compats_jetson_orins_nx = (
    "nvidia,p3509-0000+p3767-0000",
    "nvidia,p3768-0000+p3767-0000",
    "nvidia,p3509-0000+p3767-0001",
    "nvidia,p3768-0000+p3767-0001",
)

compats_jetson_orins_nano = (
    "nvidia,p3509-0000+p3767-0003",
    "nvidia,p3768-0000+p3767-0003",
    "nvidia,p3509-0000+p3767-0004",
    "nvidia,p3768-0000+p3767-0004",
    "nvidia,p3509-0000+p3767-0005",
    "nvidia,p3768-0000+p3767-0005",
)

JETSON_ORIN_PIN_DEFS = [
    (106, 'PQ.06', "tegra234-gpio", 7, 4, 'MCLK05', 'GP66', None, None),
    # Output-only (due to base board)
    (112, 'PR.04', "tegra234-gpio", 11, 17, 'UART1_RTS', 'GP72_UART1_RTS_N', None, None),
    (50, 'PH.07', "tegra234-gpio", 12, 18, 'I2S2_CLK', 'GP122', None, None),
    (108, 'PR.00', "tegra234-gpio", 13, 27, 'PWM01', 'GP68', None, None),
    (85, 'PN.01', "tegra234-gpio", 15, 22, 'GPIO27', 'GP88_PWM1', '3280000.pwm', 0),
    (9, 'PBB.01', "tegra234-gpio-aon", 16, 23, 'GPIO08', 'GP26', None, None),
    (43, 'PH.00', "tegra234-gpio", 18, 24, 'GPIO35', 'GP115', '32c0000.pwm', 0),
    (135, 'PZ.05', "tegra234-gpio", 19, 10, 'SPI1_MOSI', 'GP49_SPI1_MOSI', None, None),
    (134, 'PZ.04', "tegra234-gpio", 21, 9, 'SPI1_MISO', 'GP48_SPI1_MISO', None, None),
    (96, 'PP.04', "tegra234-gpio", 22, 25, 'GPIO17', 'GP56', None, None),
    (133, 'PZ.03', "tegra234-gpio", 23, 11, 'SPI1_CLK', 'GP47_SPI1_CLK', None, None),
    (136, 'PZ.06', "tegra234-gpio", 24, 8, 'SPI1_CS0_N', 'GP50_SPI1_CS0_N', None, None),
    (137, 'PZ.07', "tegra234-gpio", 26, 7, 'SPI1_CS1_N', 'GP51_SPI1_CS1_N', None, None),
    (1, 'PAA.01', "tegra234-gpio-aon", 29, 5, 'CAN0_DIN', 'GP18_CAN0_DIN', None, None),
    (0, 'PAA.00', "tegra234-gpio-aon", 31, 6, 'CAN0_DOUT', 'GP17_CAN0_DOUT', None, None),
    (8, 'PBB.00', "tegra234-gpio-aon", 32, 12, 'GPIO09', 'GP25', None, None),
    (2, 'PAA.02', "tegra234-gpio-aon", 33, 13, 'CAN1_DOUT', 'GP19_CAN1_DOUT', None, None),
    (53, 'PI.02', "tegra234-gpio", 35, 19, 'I2S2_FS', 'GP125', None, None),
    (113, 'PR.05', "tegra234-gpio", 36, 16, 'UART1_CTS', 'GP73_UART1_CTS_N', None, None),
    (3, 'PAA.03', "tegra234-gpio-aon", 37, 26, 'CAN1_DIN', 'GP20_CAN1_DIN', None, None),
    (52, 'PI.01', "tegra234-gpio", 38, 20, 'I2S2_DIN', 'GP124', None, None),
    (51, 'PI.00', "tegra234-gpio", 40, 21, 'I2S2_DOUT', 'GP123', None, None)
]

compats_jetson_orins = (
    'nvidia,p3737-0000+p3701-0000',
    'nvidia,p3737-0000+p3701-0004',
    'nvidia,p3737-0000+p3701-0008',
    'nvidia,p3737-0000+p3701-0005',
    'nvidia,p3737-0000+p3701-0001',
)

CLARA_AGX_XAVIER_PIN_DEFS = [
    (106, 'PQ.06', "tegra194-gpio", 7, 4, 'MCLK05', 'SOC_GPIO42', None, None),
    (112, 'PR.04', "tegra194-gpio", 11, 17, 'UART1_RTS', 'UART1_RTS', None, None),
    (51, 'PH.07', "tegra194-gpio", 12, 18, 'I2S2_CLK', 'DAP2_SCLK', None, None),
    (96, 'PP.04', "tegra194-gpio", 13, 27, 'GPIO32', 'SOC_GPIO04', None, None),
    # Older versions of L4T don't enable this PWM controller in DT, so this PWM
    # channel may not be available.
    (84, 'PN.01', "tegra194-gpio", 15, 22, 'GPIO27', 'SOC_GPIO54', '3280000.pwm', 0),
    (8, 'PBB.00', "tegra194-gpio-aon", 16, 23, 'GPIO8', 'CAN1_STB', None, None),
    (44, 'PH.00', "tegra194-gpio", 18, 24, 'GPIO35', 'SOC_GPIO12', '32c0000.pwm', 0),
    (162, 'PZ.05', "tegra194-gpio", 19, 10, 'SPI1_MOSI', 'SPI1_MOSI', None, None),
    (161, 'PZ.04', "tegra194-gpio", 21, 9, 'SPI1_MISO', 'SPI1_MISO', None, None),
    (101, 'PQ.01', "tegra194-gpio", 22, 25, 'GPIO17', 'SOC_GPIO21', None, None),
    (160, 'PZ.03', "tegra194-gpio", 23, 11, 'SPI1_CLK', 'SPI1_SCK', None, None),
    (163, 'PZ.06', "tegra194-gpio", 24, 8, 'SPI1_CS0_N', 'SPI1_CS0_N', None, None),
    (164, 'PZ.07', "tegra194-gpio", 26, 7, 'SPI1_CS1_N', 'SPI1_CS1_N', None, None),
    (3, 'PAA.03', "tegra194-gpio-aon", 29, 5, 'CAN0_DIN', 'CAN0_DIN', None, None),
    (2, 'PAA.02', "tegra194-gpio-aon", 31, 6, 'CAN0_DOUT', 'CAN0_DOUT', None, None),
    (9, 'PBB.01', "tegra194-gpio-aon", 32, 12, 'GPIO9', 'CAN1_EN', None, None),
    (0, 'PAA.00', "tegra194-gpio-aon", 33, 13, 'CAN1_DOUT', 'CAN1_DOUT', None, None),
    (54, 'PI.02', "tegra194-gpio", 35, 19, 'I2S2_FS', 'DAP2_FS', None, None),
    # Input-only (due to base board)
    (113, 'PR.05', "tegra194-gpio", 36, 16, 'UART1_CTS', 'UART1_CTS', None, None),
    (1, 'PAA.01', "tegra194-gpio-aon", 37, 26, 'CAN1_DIN', 'CAN1_DIN', None, None),
    (53, 'PI.01', "tegra194-gpio", 38, 20, 'I2S2_DIN', 'DAP2_DIN', None, None),
    (52, 'PI.00', "tegra194-gpio", 40, 21, 'I2S2_DOUT', 'DAP2_DOUT', None, None)
]
compats_clara_agx_xavier = (
    'nvidia,e3900-0000+p2888-0004',
)

JETSON_NX_PIN_DEFS = [
    (118, 'PS.04', "tegra194-gpio", 7, 4, 'GPIO09', 'AUD_MCLK', None, None),
    (112, 'PR.04', "tegra194-gpio", 11, 17, 'UART1_RTS', 'UART1_RTS', None, None),
    (127, 'PT.05', "tegra194-gpio", 12, 18, 'I2S0_SCLK', 'DAP5_SCLK', None, None),
    (149, 'PY.00', "tegra194-gpio", 13, 27, 'SPI1_SCK', 'SPI3_SCK', None, None),
    (16, 'PCC.04', "tegra194-gpio-aon", 15, 22, 'GPIO12', 'TOUCH_CLK', "c340000.pwm", 0),
    (153, 'PY.04', "tegra194-gpio", 16, 23, 'SPI1_CS1', 'SPI3_CS1_N', None, None),
    (152, 'PY.03', "tegra194-gpio", 18, 24, 'SPI1_CS0', 'SPI3_CS0_N', None, None),
    (162, 'PZ.05', "tegra194-gpio", 19, 10, 'SPI0_MOSI', 'SPI1_MOSI', None, None),
    (161, 'PZ.04', "tegra194-gpio", 21, 9, 'SPI0_MISO', 'SPI1_MISO', None, None),
    (150, 'PY.01', "tegra194-gpio", 22, 25, 'SPI1_MISO', 'SPI3_MISO', None, None),
    (160, 'PZ.03', "tegra194-gpio", 23, 11, 'SPI0_SCK', 'SPI1_SCK', None, None),
    (163, 'PZ.06', "tegra194-gpio", 24, 8, 'SPI0_CS0', 'SPI1_CS0_N', None, None),
    (164, 'PZ.07', "tegra194-gpio", 26, 7, 'SPI0_CS1', 'SPI1_CS1_N', None, None),
    (105, 'PQ.05', "tegra194-gpio", 29, 5, 'GPIO01', 'SOC_GPIO41', None, None),
    (106, 'PQ.06', "tegra194-gpio", 31, 6, 'GPIO11', 'SOC_GPIO42', None, None),
    (108, 'PR.00', "tegra194-gpio", 32, 12, 'GPIO07', 'SOC_GPIO44', '32f0000.pwm', 0),
    (84, 'PN.01', "tegra194-gpio", 33, 13, 'GPIO13', 'SOC_GPIO54', '3280000.pwm', 0),
    (130, 'PU.00', "tegra194-gpio", 35, 19, 'I2S0_FS', 'DAP5_FS', None, None),
    (113, 'PR.05', "tegra194-gpio", 36, 16, 'UART1_CTS', 'UART1_CTS', None, None),
    (151, 'PY.02', "tegra194-gpio", 37, 26, 'SPI1_MOSI', 'SPI3_MOSI', None, None),
    (129, 'PT.07', "tegra194-gpio", 38, 20, 'I2S0_DIN', 'DAP5_DIN', None, None),
    (128, 'PT.06', "tegra194-gpio", 40, 21, 'I2S0_DOUT', 'DAP5_DOUT', None, None)
]
compats_nx = (
    'nvidia,p3509-0000+p3668-0000',
    'nvidia,p3509-0000+p3668-0001',
    'nvidia,p3449-0000+p3668-0000',
    'nvidia,p3449-0000+p3668-0001',
    'nvidia,p3449-0000+p3668-0003',
)

JETSON_XAVIER_PIN_DEFS = [
    (106, 'PQ.06', "tegra194-gpio", 7, 4, 'MCLK05', 'SOC_GPIO42', None, None),
    # added Pin 8 == status LED red
    (110, 'PR.02', "tegra194-gpio", 8, None, 'UART1_TX', 'UART1_TX', None, None),
    # added PIN 10 for light trigger input
    (111, 'PR.03', "tegra194-gpio", 10, None, 'UART1_RX', 'UART1_RX', None, None),
    # Pin 11 == status LED green
    (112, 'PR.04', "tegra194-gpio", 11, 17, 'UART1_RTS', 'UART1_RTS', None, None),
    # Pin12 == start illumination LED lights
    (51, 'PH.07', "tegra194-gpio", 12, 18, 'I2S2_CLK', 'DAP2_SCLK', None, None),
    (108, 'PR.00', "tegra194-gpio", 13, 27, 'PWM01', 'SOC_GPIO44', '32f0000.pwm', 0),
    # Older versions of L4T don'Pt enable this PWM controller in DT, so this PWM
    # channel may not be available.
    (84, 'PN.01', "tegra194-gpio", 15, 22, 'GPIO27', 'SOC_GPIO54', '3280000.pwm', 0),
    (8, 'BB.00', "tegra194-gpio-aon", 16, 23, 'GPIO8', 'CAN1_STB', None, None),
    (44, 'PH.00', "tegra194-gpio", 18, 24, 'GPIO35', 'SOC_GPIO12', '32c0000.pwm', 0),
    (162, 'PZ.05', "tegra194-gpio", 19, 10, 'SPI1_MOSI', 'SPI1_MOSI', None, None),
    (161, 'PZ.04', "tegra194-gpio", 21, 9, 'SPI1_MISO', 'SPI1_MISO', None, None),
    (101, 'PQ.01', "tegra194-gpio", 22, 25, 'GPIO17', 'SOC_GPIO21', None, None),
    (160, 'PZ.03', "tegra194-gpio", 23, 11, 'SPI1_CLK', 'SPI1_SCK', None, None),
    (163, 'PZ.06', "tegra194-gpio", 24, 8, 'SPI1_CS0_N', 'SPI1_CS0_N', None, None),
    (164, 'PZ.07', "tegra194-gpio", 26, 7, 'SPI1_CS1_N', 'SPI1_CS1_N', None, None),
    (3, 'PAA.03', "tegra194-gpio-aon", 29, 5, 'CAN0_DIN', 'CAN0_DIN', None, None),
    (2, 'PAA.02', "tegra194-gpio-aon", 31, 6, 'CAN0_DOUT', 'CAN0_DOUT', None, None),
    (9, 'PBB.01', "tegra194-gpio-aon", 32, 12, 'GPIO9', 'CAN1_EN', None, None),
    (0, 'PAA.00', "tegra194-gpio-aon", 33, 13, 'CAN1_DOUT', 'CAN1_DOUT', None, None),
    (54, 'PI.02', "tegra194-gpio", 35, 19, 'I2S2_FS', 'DAP2_FS', None, None),
    # Input-only (due to base board)
    (113, 'PR.05', "tegra194-gpio", 36, 16, 'UART1_CTS', 'UART1_CTS', None, None),
    (1, 'PAA.01', "tegra194-gpio-aon", 37, 26, 'CAN1_DIN', 'CAN1_DIN', None, None),
    (53, 'PI.01', "tegra194-gpio", 38, 20, 'I2S2_DIN', 'DAP2_DIN', None, None),
    (52, 'PI.00', "tegra194-gpio", 40, 21, 'I2S2_DOUT', 'DAP2_DOUT', None, None)
]
compats_xavier = (
    'nvidia,p2972-0000',
    'nvidia,p2972-0006',
    'nvidia,jetson-xavier',
    'nvidia,galen-industrial',
    'nvidia,jetson-xavier-industrial',
)

JETSON_TX2_NX_PIN_DEFS = [
    (76, 'PJ.04', "tegra-gpio", 7, 4, 'GPIO09', 'AUD_MCLK', None, None),
    (28, 'PW.04', "tegra-gpio-aon", 11, 17, 'UART1_RTS', 'UART3_RTS', None, None),
    (72, 'PJ.00', "tegra-gpio", 12, 18, 'I2S0_SCLK', 'DAP1_SCLK', None, None),
    (17, 'PV.01', "tegra-gpio-aon", 13, 27, 'SPI1_SCK', 'GPIO_SEN1', None, None),
    (18, 'PC.02', "tegra-gpio", 15, 22, 'GPIO12', 'DAP2_DOUT', None, None),
    (19, 'PC.03', "tegra-gpio", 16, 23, 'SPI1_CS1', 'DAP2_DIN', None, None),
    (20, 'PV.04', "tegra-gpio-aon", 18, 24, 'SPI1_CS0', 'GPIO_SEN4', None, None),
    (58, 'PH.02', "tegra-gpio", 19, 10, 'SPI0_MOSI', 'GPIO_WAN7', None, None),
    (57, 'PH.01', "tegra-gpio", 21, 9, 'SPI0_MISO', 'GPIO_WAN6', None, None),
    (18, 'PV.02', "tegra-gpio-aon", 22, 25, 'SPI1_MISO', 'GPIO_SEN2', None, None),
    (56, 'PH.00', "tegra-gpio", 23, 11, 'SPI1_CLK', 'GPIO_WAN5', None, None),
    (59, 'PH.03', "tegra-gpio", 24, 8, 'SPI0_CS0', 'GPIO_WAN8', None, None),
    (163, 'PY.03', "tegra-gpio", 26, 7, 'SPI0_CS1', 'GPIO_MDM4', None, None),
    (105, 'PN.01', "tegra-gpio", 29, 5, 'GPIO01', 'GPIO_CAM2', None, None),
    (50, 'PEE.02', "tegra-gpio-aon", 31, 6, 'GPIO11', 'TOUCH_CLK', None, None),
    (8, 'PU.00', "tegra-gpio-aon", 32, 12, 'GPIO07', 'GPIO_DIS0', '3280000.pwm', 0),
    (13, 'PU.05', "tegra-gpio-aon", 33, 13, 'GPIO13', 'GPIO_DIS5', '32a0000.pwm', 0),
    (75, 'PJ.03', "tegra-gpio", 35, 19, 'I2S0_FS', 'DAP1_FS', None, None),
    (29, 'PW.05', "tegra-gpio-aon", 36, 16, 'UART1_CTS', 'UART3_CTS', None, None),
    (19, 'PV.03', "tegra-gpio-aon", 37, 26, 'SPI1_MOSI', 'GPIO_SEN3', None, None),
    (74, 'PJ.02', "tegra-gpio", 38, 20, 'I2S0_DIN', 'DAP1_DIN', None, None),
    (73, 'PJ.01', "tegra-gpio", 40, 21, 'I2S0_DOUT', 'DAP1_DOUT', None, None)
]
compats_tx2_nx = (
    'nvidia,p3509-0000+p3636-0001',
)

JETSON_TX2_PIN_DEFS = [
    (76, 'PJ.04', "tegra-gpio", 7, 4, 'PAUDIO_MCLK', 'AUD_MCLK', None, None),
    # Output-only (due to base board)
    (146, 'PT.02', "tegra-gpio", 11, 17, 'PUART0_RTS', 'UART1_RTS', None, None),
    (72, 'PJ.00', "tegra-gpio", 12, 18, 'PI2S0_CLK', 'DAP1_SCLK', None, None),
    (77, 'PJ.05', "tegra-gpio", 13, 27, 'PGPIO20_AUD_INT', 'GPIO_AUD0', None, None),
    (15, 'GPIO_EXP_P16', "tca9539", 15, 22, 'GPIO_EXP_P17', 'GPIO_EXP_P17', None, None),
    # Input-only (due to module):
    (40,  'PAA.00', "tegra-gpio-aon", 16, 23, 'AO_DMIC_IN_DAT', 'CAN_GPIO0', None, None),
    (161, 'PY.01', "tegra-gpio", 18, 24, 'GPIO16_MDM_WAKE_AP', 'GPIO_MDM2', None, None),
    (109, 'PN.05', "tegra-gpio", 19, 10, 'SPI1_MOSI', 'GPIO_CAM6', None, None),
    (108, 'PN.04', "tegra-gpio", 21, 9, 'SPI1_MISO', 'GPIO_CAM5', None, None),
    (14,  'GPIO_EXP_P16', "tca9539", 22, 25, 'GPIO_EXP_P16', 'GPIO_EXP_P16', None, None),
    (107, 'PN.03', "tegra-gpio", 23, 11, 'SPI1_CLK', 'GPIO_CAM4', None, None),
    (110, 'PN.06', "tegra-gpio", 24, 8, 'SPI1_CS0', 'GPIO_CAM7', None, None),
    # Board pin 26 is not available on this board
    (78, 'PJ.06', "tegra-gpio", 29, 5, 'GPIO19_AUD_RST', 'GPIO_AUD1', None, None),
    (42, 'PAA.02', "tegra-gpio-aon", 31, 6, 'GPIO9_MOTION_INT', 'CAN_GPIO2', None, None),
    # Output-only (due to module):
    (41, 'PAA.01', "tegra-gpio-aon", 32, 12, 'AO_DMIC_IN_CLK', 'CAN_GPIO1', None, None),
    (69, 'PI.05', "tegra-gpio", 33, 13, 'GPIO11_AP_WAKE_BT', 'GPIO_PQ5', None, None),
    (75, 'PJ.03', "tegra-gpio", 35, 19, 'I2S0_LRCLK', 'DAP1_FS', None, None),
    # Input-only (due to base board) IF NVIDIA debug card NOT plugged in
    # Output-only (due to base board) IF NVIDIA debug card plugged in
    (147, 'PT.03', "tegra-gpio", 36, 16, 'UART0_CTS', 'UART1_CTS', None, None),
    (68, 'PI.04', "tegra-gpio", 37, 26, 'GPIO8_ALS_PROX_INT', 'GPIO_PQ4', None, None),
    (74, 'PJ.02', "tegra-gpio", 38, 20, 'I2S0_SDIN', 'DAP1_DIN', None, None),
    (73, 'PJ.01', "tegra-gpio", 40, 21, 'I2S0_SDOUT', 'DAP1_DOUT', None, None)
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
    (216, '', "tegra-gpio", 7, 4, 'AUDIO_MCLK', 'AUD_MCLK', None, None),
    # Output-only (due to base board)
    (162, '', "tegra-gpio", 11, 17, 'UART0_RTS', 'UART1_RTS', None, None),
    (11, '',  "tegra-gpio", 12, 18, 'I2S0_CLK', 'DAP1_SCLK', None, None),
    (38, '', "tegra-gpio", 13, 27, 'GPIO20_AUD_INT', 'GPIO_PE6', None, None),
    (15, '', "tca9539", 15, 22, 'GPIO_EXP_P17', 'GPIO_EXP_P17', None, None),
    (37, '', "tegra-gpio", 16, 23, 'AO_DMIC_IN_DAT', 'DMIC3_DAT', None, None),
    (184, '', "tegra-gpio", 18, 24, 'GPIO16_MDM_WAKE_AP', 'MODEM_WAKE_AP', None, None),
    (16, '', "tegra-gpio", 19, 10, 'SPI1_MOSI', 'SPI1_MOSI', None, None),
    (17, '', "tegra-gpio", 21, 9, 'SPI1_MISO', 'SPI1_MISO', None, None),
    (14, '', "tca9539", 22, 25, 'GPIO_EXP_P16', 'GPIO_EXP_P16', None, None),
    (18, '', "tegra-gpio", 23, 11, 'SPI1_CLK', 'SPI1_SCK', None, None),
    (19, '', "tegra-gpio", 24, 8, 'SPI1_CS0', 'SPI1_CS0', None, None),
    (20, '', "tegra-gpio", 26, 7, 'SPI1_CS1', 'SPI1_CS1', None, None),
    (219, '', "tegra-gpio", 29, 5, 'GPIO19_AUD_RST', 'GPIO_X1_AUD', None, None),
    (186, '', "tegra-gpio", 31, 6, 'GPIO9_MOTION_INT', 'MOTION_INT', None, None),
    (36, '', "tegra-gpio", 32, 12, 'AO_DMIC_IN_CLK', 'DMIC3_CLK', None, None),
    (63, '', "tegra-gpio", 33, 13, 'GPIO11_AP_WAKE_BT', 'AP_WAKE_NFC', None, None),
    (8, '', "tegra-gpio", 35, 19, 'I2S0_LRCLK', 'DAP1_FS', None, None),
    # Input-only (due to base board) IF NVIDIA debug card NOT plugged in
    # Input-only (due to base board) (always reads fixed value) IF NVIDIA debug card plugged in
    (163, '', "tegra-gpio", 36, 16, 'UART0_CTS', 'UART1_CTS', None, None),
    (187, '',  "tegra-gpio", 37, 26, 'GPIO8_ALS_PROX_INT', 'ALS_PROX_INT', None, None),
    (9, '', "tegra-gpio", 38, 20, 'I2S0_SDIN', 'DAP1_DIN', None, None),
    (10, '', "tegra-gpio", 40, 21, 'I2S0_SDOUT', 'DAP1_DOUT', None, None)
]
compats_tx1 = (
    'nvidia,p2371-2180',
    'nvidia,jetson-cv',
)

JETSON_NANO_PIN_DEFS = [
    (216,  '', "tegra-gpio", 7, 4, 'GPIO9', 'AUD_MCLK', None, None),
    (50,  '', "tegra-gpio", 11, 17, 'UART1_RTS', 'UART2_RTS', None, None),
    (79, '',  "tegra-gpio", 12, 18, 'I2S0_SCLK', 'DAP4_SCLK', None, None),
    (14,  '', "tegra-gpio", 13, 27, 'SPI1_SCK', 'SPI2_SCK', None, None),
    (194,  '', "tegra-gpio", 15, 22, 'GPIO12', 'LCD_TE', None, None),
    (232,  '', "tegra-gpio", 16, 23, 'SPI1_CS1', 'SPI2_CS1', None, None),
    (15,  '', "tegra-gpio", 18, 24, 'SPI1_CS0', 'SPI2_CS0', None, None),
    (16,  '', "tegra-gpio", 19, 10, 'SPI0_MOSI', 'SPI1_MOSI', None, None),
    (17,  '', "tegra-gpio", 21, 9, 'SPI0_MISO', 'SPI1_MISO', None, None),
    (13,  '', "tegra-gpio", 22, 25, 'SPI1_MISO', 'SPI2_MISO', None, None),
    (18,  '', "tegra-gpio", 23, 11, 'SPI0_SCK', 'SPI1_SCK', None, None),
    (19,  '', "tegra-gpio", 24, 8, 'SPI0_CS0', 'SPI1_CS0', None, None),
    (20,  '', "tegra-gpio", 26, 7, 'SPI0_CS1', 'SPI1_CS1', None, None),
    (149,  '', "tegra-gpio", 29, 5, 'GPIO01', 'CAM_AF_EN', None, None),
    (200,  '', "tegra-gpio", 31, 6, 'GPIO11', 'GPIO_PZ0', None, None),
    # Older versions of L4T have a DT bug which instantiates a bogus device
    # which prevents this library from using this PWM channel.
    (168,  '', "tegra-gpio", 32, 12, 'GPIO07', 'LCD_BL_PW', '7000a000.pwm', 0),
    (38,  '', "tegra-gpio", 33, 13, 'GPIO13', 'GPIO_PE6', '7000a000.pwm', 2),
    (76,  '', "tegra-gpio", 35, 19, 'I2S0_FS', 'DAP4_FS', None, None),
    (51,  '', "tegra-gpio", 36, 16, 'UART1_CTS', 'UART2_CTS', None, None),
    (12,  '', "tegra-gpio", 37, 26, 'SPI1_MOSI', 'SPI2_MOSI', None, None),
    (77,  '', "tegra-gpio", 38, 20, 'I2S0_DIN', 'DAP4_DIN', None, None),
    (78,  '', "tegra-gpio", 40, 21, 'I2S0_DOUT', 'DAP4_DOUT', None, None)
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
    JETSON_ORIN_NANO: (
        JETSON_ORIN_NX_PIN_DEFS,
        {
            'P1_REVISION': 1,
            'RAM': '32768M, 65536M',
            'REVISION': 'Unknown',
            'TYPE': 'JETSON_ORIN_NANO',
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
    # @channel the pin number in specified mode (board or bcm)
    # @chip_fd the file descriptor of the chip 
    # @line_handle the file descriptor of the line
    # @line_offset Linux GPIO pin number (line offset inside chip, not global)
    # @direction the direction of a pin is configured (in or out)
    # @edge rising and/or falling edge being monitored
    # @consumer consumer label
    # @gpio_name Linux exported GPIO name
    # @gpio_chip GPIO chip name/instance
    def __init__(self, channel, line_offset, gpio_name, gpio_chip, pwm_chip_dir, pwm_id):
        self.channel = channel
        self.chip_fd = None
        self.line_handle = None
        self.line_offset = line_offset
        self.direction = None
        self.edge = None
        self.consumer = "Jetson-gpio"
        self.gpio_name = gpio_name
        self.gpio_chip = gpio_chip
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
            warn_if_not_carrier_board('3509', '3768')
            return JETSON_ORIN_NX
        elif matches(compats_jetson_orins_nano):
            warn_if_not_carrier_board('3509', '3768')
            return JETSON_ORIN_NANO

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

# @brief Retrieve all the data before connecting to any ports
# @param[out] model: model number of an Jetson platform
# @param[out] jetson_info:
# @param[out] channel_info: the information related to pin/line, in
def get_data():
    model = get_model()

    pin_defs, jetson_info = jetson_gpio_data[model]
    gpio_chip_dirs = {}
    gpio_chip_base = {}
    gpio_chip_ngpio = {}
    pwm_dirs = {}

    sysfs_prefixes = ['/sys/devices/', '/sys/devices/platform/', '/sys/bus/platform/devices/']

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
            x[0],
            x[1],
            x[2],
            pwm_chip_dir=pwm_dirs.get(x[7], None),
            pwm_id=x[8]) for x in pin_defs}

    channel_data = {
        'BOARD': model_data(3, pin_defs),
        'BCM': model_data(4, pin_defs),
        'CVM': model_data(5, pin_defs),
        'TEGRA_SOC': model_data(6, pin_defs),
    }

    return model, jetson_info, channel_data

