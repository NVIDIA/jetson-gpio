# Add support for Jetson Orin Nano Super variant

## Problem

The Jetson.GPIO library currently fails to recognize Jetson Orin Nano "Super" developer kit variants, causing GPIO operations to fail with the error:

```
Exception: Could not determine Jetson model
```

This affects users of the newer Jetson Orin Nano Engineering Reference Developer Kit Super hardware.

## Root Cause

The Super variants report device tree compatible strings with a `-super` suffix:
- `nvidia,p3509-0000+p3767-0005-super`
- `nvidia,p3768-0000+p3767-0005-super`

However, the GPIO library's device recognition only includes the non-suffixed versions:
- `nvidia,p3509-0000+p3767-0005`
- `nvidia,p3768-0000+p3767-0005`

## Solution

This PR adds the Super variant compatible strings to the `compats_jetson_orins_nano` tuple in `gpio_pin_data.py`, enabling GPIO library functionality for these hardware variants.

## Hardware Details

- **Model**: NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super
- **Device Tree Model**: `NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super`
- **Compatible String**: `nvidia,p3768-0000+p3767-0005-super nvidia,p3767-0005 nvidia,tegra234`

## Testing

Tested on actual Super variant hardware:

**Before the fix:**
```python
import Jetson.GPIO as GPIO
# Exception: Could not determine Jetson model
```

**After the fix:**
```python
import Jetson.GPIO as GPIO
print(f'GPIO modes available: BOARD={GPIO.BOARD}, BCM={GPIO.BCM}')
print(f'Tegra modes available: TEGRA_SOC={GPIO.TEGRA_SOC}, CVM={GPIO.CVM}')
# ✅ All GPIO functionality working
```

## Impact

- **Backward Compatible**: No changes to existing hardware support
- **Minimal**: Only adds two lines of compatible strings
- **Safe**: Uses the same pin configuration as standard Orin Nano variants
- **Community Benefit**: Enables GPIO functionality for all Super variant owners

## Related Issues

Fixes #120

## Files Changed

- `lib/python/Jetson/GPIO/gpio_pin_data.py`: Added Super variant compatible strings

## Verification

The fix has been tested with:
- All GPIO pin modes (BOARD, BCM, TEGRA_SOC, CVM)
- GPIO input/output operations
- Pin numbering verification
- Hardware abstraction layer functionality

This change enables the growing Super variant user community to fully utilize the Jetson.GPIO library without modification.