import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'python'))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_gpio_hardware(mocker):
    """Mock the GPIO hardware interface for testing without actual hardware."""
    mock_hw = mocker.MagicMock()
    mock_hw.is_jetson = True
    mock_hw.get_model = mocker.MagicMock(return_value="JETSON_NANO")
    mock_hw.get_jetson_board_revision = mocker.MagicMock(return_value="A02")
    return mock_hw


@pytest.fixture
def mock_gpio_permissions(mocker, temp_dir):
    """Mock GPIO permissions and sysfs paths."""
    gpio_path = temp_dir / "sys" / "class" / "gpio"
    gpio_path.mkdir(parents=True, exist_ok=True)
    
    mocker.patch.dict(os.environ, {
        "JETSON_GPIO_TEST": "1",
        "JETSON_GPIO_SYSFS": str(gpio_path)
    })
    
    return gpio_path


@pytest.fixture
def gpio_cleanup():
    """Ensure GPIO cleanup after each test."""
    yield
    try:
        import Jetson.GPIO as GPIO
        GPIO.cleanup()
    except Exception:
        pass


@pytest.fixture
def mock_config():
    """Provide a mock configuration dictionary."""
    return {
        "debug": False,
        "warnings": True,
        "mode": "BOARD",
        "pwm_frequency": 2000,
        "cleanup_on_exit": True
    }


@pytest.fixture
def sample_pin_data():
    """Provide sample GPIO pin data for testing."""
    return {
        "board_pins": {
            7: {"name": "GPIO_PZ0", "gpio": 216, "pwm": None},
            11: {"name": "GPIO_PQ5", "gpio": 133, "pwm": None},
            12: {"name": "GPIO_PE6", "gpio": 38, "pwm": 2},
            13: {"name": "GPIO_PQ6", "gpio": 134, "pwm": None},
            15: {"name": "GPIO_PH1", "gpio": 57, "pwm": None}
        },
        "bcm_pins": {
            4: {"name": "GPIO_PZ0", "gpio": 216, "pwm": None},
            17: {"name": "GPIO_PQ5", "gpio": 133, "pwm": None},
            18: {"name": "GPIO_PE6", "gpio": 38, "pwm": 2},
            27: {"name": "GPIO_PQ6", "gpio": 134, "pwm": None},
            22: {"name": "GPIO_PH1", "gpio": 57, "pwm": None}
        }
    }


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset imported modules to ensure clean state between tests."""
    modules_to_remove = [
        module for module in sys.modules 
        if module.startswith(('Jetson', 'RPi'))
    ]
    for module in modules_to_remove:
        del sys.modules[module]