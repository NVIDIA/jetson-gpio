# Pin Numbering Modes
BOARD = 10
BCM = 11
TEGRA_SOC = 1000
CVM = 1001

# The constants and their offsets are implemented to prevent HIGH from being
# used in place of other variables (ie. HIGH and RISING should not be
# interchangeable)

# Pull up/down options
_PUD_OFFSET = 20
PUD_OFF = 0 + _PUD_OFFSET
PUD_DOWN = 1 + _PUD_OFFSET
PUD_UP = 2 + _PUD_OFFSET

HIGH = 1
LOW = 0

# Edge possibilities
# These values (with _EDGE_OFFSET subtracted) must match gpio_event.py:*_EDGE
_EDGE_OFFSET = 30
RISING = 1 + _EDGE_OFFSET
FALLING = 2 + _EDGE_OFFSET
BOTH = 3 + _EDGE_OFFSET

# GPIO directions. UNKNOWN constant is for gpios that are not yet setup
UNKNOWN = -1
OUT = 0
IN = 1
HARD_PWM = 43
