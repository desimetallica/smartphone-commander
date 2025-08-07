import pytest
from unittest.mock import patch, MagicMock

from smartphone_cli import DeviceManager

@pytest.fixture
def mock_devices():
    return ["device1", "device2"]

@pytest.fixture
def device_manager(tmp_path, mock_devices):
    with patch("smartphone_cli.DeviceManager.get_connected_devices", return_value=mock_devices):
        dm = DeviceManager(logfile_path=str(tmp_path / "test.log"))
        yield dm

def test_get_connected_devices_returns_devices(device_manager, mock_devices):
    assert device_manager.devices == mock_devices

def test_log_writes_to_file(device_manager, tmp_path):
    log_file = tmp_path / "test.log"
    device_manager.logfile_path = str(log_file)
    device_manager.log("Test message")
    with open(log_file) as f:
        content = f.read()
    assert "Test message" in content

@patch("smartphone_cli.subprocess.check_output")
def test_get_device_info_returns_dict(mock_check_output, device_manager):
    mock_check_output.return_value = "test_value"
    info = device_manager.get_device_info("device1")
    assert set(info.keys()) == {"brand", "device", "name", "model"}
    assert all(v == "test_value" for v in info.values())

@patch("smartphone_cli.subprocess.check_output")
def test_get_airplane_mode_status(mock_check_output, device_manager):
    mock_check_output.return_value = "enabled"
    status = device_manager.get_airplane_mode_status("device1")
    assert status == "enabled"

@patch("smartphone_cli.subprocess.run")
def test_set_airplane_mode_enable(mock_run, device_manager):
    device_manager.set_airplane_mode("device1", True)
    mock_run.assert_called_with(
        ["adb", "-s", "device1", "shell", "cmd", "connectivity", "airplane-mode", "enable"],
        check=True
    )

@patch("smartphone_cli.subprocess.run")
def test_set_airplane_mode_disable(mock_run, device_manager):
    device_manager.set_airplane_mode("device1", False)
    mock_run.assert_called_with(
        ["adb", "-s", "device1", "shell", "cmd", "connectivity", "airplane-mode", "disable"],
        check=True
    )

@patch("smartphone_cli.DeviceManager.get_airplane_mode_status")
@patch("smartphone_cli.DeviceManager.set_airplane_mode")
def test_auto_toggle_airplane_mode_enable(mock_set, mock_status, device_manager):
    mock_status.return_value = "disabled"
    device_manager.auto_toggle_airplane_mode("device1")
    mock_set.assert_called_with("device1", True)

@patch("smartphone_cli.DeviceManager.get_airplane_mode_status")
@patch("smartphone_cli.DeviceManager.set_airplane_mode")
def test_auto_toggle_airplane_mode_disable(mock_set, mock_status, device_manager):
    mock_status.return_value = "enabled"
    device_manager.auto_toggle_airplane_mode("device1")
    mock_set.assert_called_with("device1", False)

@patch("smartphone_cli.subprocess.run")
def test_reboot_device(mock_run, device_manager):
    device_manager.reboot_device("device1")
    mock_run.assert_called_with(["adb", "-s", "device1", "reboot"], check=True)

@patch("smartphone_cli.DeviceManager.get_device_info")
@patch("smartphone_cli.DeviceManager.get_airplane_mode_status")
@patch("smartphone_cli.DeviceManager.monitor_connectivity_type")
def test_check_device_status(mock_monitor, mock_airplane, mock_info, device_manager):
    mock_info.return_value = {"brand": "b", "device": "d", "name": "n", "model": "m"}
    device_manager.check_device_status("device1")
    mock_info.assert_called_with("device1")
    mock_airplane.assert_called_with("device1")
    mock_monitor.assert_called_with("device1")

@patch("smartphone_cli.subprocess.check_output")
def test_monitor_connectivity_type_found(mock_check_output, device_manager):
    mock_check_output.return_value = "accessNetworkTechnology=LTE"
    device_manager.monitor_connectivity_type("device1")
    # Should log "Current connectivity: 4G (LTE)"

@patch("smartphone_cli.subprocess.check_output")
def test_monitor_connectivity_type_not_found(mock_check_output, device_manager):
    mock_check_output.return_value = "no relevant info"
    device_manager.monitor_connectivity_type("device1")
    # Should log "Field 'accessNetworkTechnology' not found."