import pytest
import sys
import os


class TestSetupValidation:
    """Validation tests to ensure the testing infrastructure is properly configured."""
    
    def test_python_path_configured(self):
        """Test that the Python path includes the library directory."""
        lib_path = os.path.join(os.path.dirname(__file__), '..', '..', 'lib', 'python')
        lib_path = os.path.abspath(lib_path)
        assert any(os.path.abspath(path) == lib_path for path in sys.path), \
            "Library path not found in sys.path"
    
    def test_fixtures_available(self, temp_dir, mock_config, sample_pin_data):
        """Test that all required fixtures are available and working."""
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        assert isinstance(mock_config, dict)
        assert "debug" in mock_config
        assert "mode" in mock_config
        
        assert isinstance(sample_pin_data, dict)
        assert "board_pins" in sample_pin_data
        assert "bcm_pins" in sample_pin_data
    
    def test_mock_gpio_fixtures(self, mock_gpio_hardware, mock_gpio_permissions):
        """Test GPIO-specific fixtures."""
        assert mock_gpio_hardware.is_jetson is True
        assert mock_gpio_hardware.get_model() == "JETSON_NANO"
        assert mock_gpio_hardware.get_jetson_board_revision() == "A02"
        
        assert mock_gpio_permissions.exists()
        assert mock_gpio_permissions.is_dir()
    
    @pytest.mark.unit
    def test_unit_marker(self):
        """Test that the unit marker is properly configured."""
        assert True
    
    @pytest.mark.integration
    def test_integration_marker(self):
        """Test that the integration marker is properly configured."""
        assert True
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that the slow marker is properly configured."""
        assert True
    
    def test_coverage_configured(self):
        """Test that coverage is properly configured."""
        try:
            import coverage
            assert True
        except ImportError:
            pytest.fail("Coverage module not installed")
    
    def test_pytest_mock_available(self):
        """Test that pytest-mock is available."""
        try:
            import pytest_mock
            assert True
        except ImportError:
            pytest.fail("pytest-mock module not installed")