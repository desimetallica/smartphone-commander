#!/usr/bin/env python3

import os
import subprocess
import sys
import re
import argparse
from rich.console import Console
from rich.table import Table

class DeviceManager:

    def __init__(self, logfile_path="/tmp/smartphone_cli.log"):
        self.logfile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), logfile_path)
        self.devices = self.get_connected_devices()

    def log(self, message):
        import datetime
        import inspect
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        caller = inspect.stack()[1]
        func_name = caller.function
        class_name = self.__class__.__name__
        log_line = f"[{timestamp}] [{class_name}.{func_name}] {message}"
        with open(self.logfile_path, "a") as f:
            f.write(log_line + "\n")
        print(log_line)

    def list_devices(self):
        console = Console()
        self.log("Listing all connected devices:")
        table = Table(title="Connected Devices")
        table.add_column("Index", style="cyan", justify="right")
        table.add_column("Serial", style="magenta")
        table.add_column("Brand", style="green")
        table.add_column("Device", style="yellow")
        table.add_column("Name", style="white")
        table.add_column("Model", style="blue")
        for idx, dev in enumerate(self.devices):
            info = self.get_device_info(dev)
            table.add_row(str(idx), dev, info['brand'], info['device'], info['name'], info['model'])
            self.log(f"Device {dev} | Brand: {info['brand']} | Device: {info['device']} | Name: {info['name']} | Model: {info['model']}")
        console.print(table)

    def get_connected_devices(self):
        try:
            output = subprocess.check_output(["adb", "devices"], encoding="utf-8")
            lines = output.strip().splitlines()[1:]
            devices = [line.split()[0] for line in lines if "\tdevice" in line]
            if not devices:
                self.log("No device connected via ADB.")
                # sys.exit(1)
            return devices
        except subprocess.CalledProcessError:
            self.log("Error running 'adb devices'.")
            # sys.exit(1)

    def get_device_info(self, device):
        def get_prop(prop):
            try:
                return subprocess.check_output([
                    "adb", "-s", device, "shell", "getprop", prop
                ], encoding="utf-8").strip()
            except Exception:
                return "Unknown"
        return {
            "brand": get_prop("ro.product.brand"),
            "device": get_prop("ro.product.device"),
            "name": get_prop("ro.product.name"),
            "model": get_prop("ro.product.model")
        }

    def select_device(self, device_id=None):
        console = Console()
        if device_id and device_id in self.devices:
            info = self.get_device_info(device_id)
            self.log(f"Using device: {device_id} | Brand: {info['brand']} | Device: {info['device']} | Name: {info['name']} | Model: {info['model']}")
            return device_id
        elif device_id and device_id not in self.devices:
            self.log(f"Device {device_id} not found among connected devices.")
            sys.exit(1)
        if len(self.devices) == 1:
            info = self.get_device_info(self.devices[0])
            self.log(f"One device found: {self.devices[0]} | Brand: {info['brand']} | Device: {info['device']} | Name: {info['name']} | Model: {info['model']}")
            return self.devices[0]
        else:
            self.log("Multiple devices found:")
            table = Table(title="Connected Devices")
            table.add_column("Index", style="cyan", justify="right")
            table.add_column("Serial", style="magenta")
            table.add_column("Brand", style="green")
            table.add_column("Device", style="yellow")
            table.add_column("Name", style="white")
            table.add_column("Model", style="blue")
            device_infos = []
            for idx, dev in enumerate(self.devices):
                info = self.get_device_info(dev)
                device_infos.append(info)
                table.add_row(str(idx), dev, info['brand'], info['device'], info['name'], info['model'])
            console.print(table)
            while True:
                try:
                    choice = input("Select device index: ")
                    idx = int(choice)
                    if 0 <= idx < len(self.devices):
                        self.log(f"Selected device: {self.devices[idx]}")
                        return self.devices[idx]
                    else:
                        print("Invalid selection. Try again.")
                except ValueError:
                    print("Please enter a valid index.")

    def get_airplane_mode_status(self, device):
        try:
            output = subprocess.check_output(
                ["adb", "-s", device, "shell", "cmd", "connectivity", "airplane-mode"],
                encoding="utf-8"
            ).strip()
            self.log(f"Current airplane mode: {output}")
            return output
        except subprocess.CalledProcessError as e:
            self.log("Error getting airplane mode status.")
            self.log(f"Message: {e}")
            sys.exit(1)

    def set_airplane_mode(self, device, enable: bool):
        state = "enable" if enable else "disable"
        try:
            subprocess.run(
                ["adb", "-s", device, "shell", "cmd", "connectivity", "airplane-mode", state],
                check=True
            )
            self.log(f"Airplane mode {'enabled' if enable else 'disabled'}.")
        except subprocess.CalledProcessError as e:
            self.log(f"Error setting airplane mode to '{state}'.")
            self.log(f"Message: {e}")

    def auto_toggle_airplane_mode(self, device):
        status = self.get_airplane_mode_status(device)
        if "enabled" in status:
            self.log("Airplane mode already enabled. Disabling...")
            self.set_airplane_mode(device, False)
        elif "disabled" in status:
            self.log("Airplane mode disabled. Enabling...")
            self.set_airplane_mode(device, True)
        else:
            self.log("Unrecognized airplane mode status.")

    def reboot_device(self, device):
        self.log("Starting device reboot...")
        try:
            subprocess.run(["adb", "-s", device, "reboot"], check=True)
            self.log("Device rebooted successfully.")
        except subprocess.CalledProcessError as e:
            self.log("Error rebooting device.")
            self.log(f"Message: {e}")

    def check_device_status(self, device=None):
        console = Console()
        if device is not None:
            info = self.get_device_info(device)
            self.log(f"Device info: Serial: {device} | Brand: {info['brand']} | Device: {info['device']} | Name: {info['name']}")
            self.log("Checking device status...")
            self.get_airplane_mode_status(device)
            self.monitor_connectivity_type(device)
        else:
            # Multiple devices: show table with status for all
            table = Table(title="Devices Status")
            table.add_column("Index", style="cyan", justify="right")
            table.add_column("Serial", style="magenta")
            table.add_column("Brand", style="green")
            table.add_column("Device", style="yellow")
            table.add_column("Name", style="white")
            table.add_column("Model", style="blue")
            table.add_column("Airplane Mode")
            table.add_column("Connectivity", style="bright_cyan")
            string_type_map = {
                "NR": "5G (NR)",
                "LTE": "4G (LTE)",
                "LTE_CA": "4G+ (LTE CA)",
                "HSPA": "3G (HSPA)",
                "UMTS": "3G (UMTS)",
                "EDGE": "2G (EDGE)",
                "GPRS": "2G (GPRS)"
            }
            for idx, dev in enumerate(self.devices):
                info = self.get_device_info(dev)
                # Airplane mode
                airplane = self.get_airplane_mode_status(dev)
                # Connectivity
                connectivity = self.monitor_connectivity_type(dev)
                print(connectivity)
                if airplane == "enabled":
                    table.add_row(
                        str(idx), dev, info['brand'], info['device'], info['name'], info['model'], "[red]" + airplane + "✈️[/red]", "[red]" + connectivity + "[/red]"
                    )
                else:
                    table.add_row(
                        str(idx), dev, info['brand'], info['device'], info['name'], info['model'], airplane, connectivity + "📡"
                    )
            console.print(table)

    def monitor_connectivity_type(self, device):
        self.log("Checking data connection status...")
        string_type_map = {
            "NR": "5G (NR)",
            "LTE": "4G (LTE)",
            "LTE_CA": "4G+ (LTE CA)",
            "HSPA": "3G (HSPA)",
            "UMTS": "3G (UMTS)",
            "EDGE": "2G (EDGE)",
            "GPRS": "2G (GPRS)"
        }
        try:
            output = subprocess.check_output(
                ["adb", "-s", device, "shell", "dumpsys", "telephony.registry"],
                encoding="utf-8",
                stderr=subprocess.DEVNULL
            )
            matches = re.findall(r"accessNetworkTechnology=([A-Z_]+)", output)
            if matches:
                latest = matches[-1].strip().upper()
                result = string_type_map.get(latest, "Unknown")
                self.log(f"Current connectivity: {result}")
                return result
            else:
                self.log("Field 'accessNetworkTechnology' not found.")
        except subprocess.CalledProcessError as e:
            self.log(f"Error running adb: {e}")

def main():
    parser = argparse.ArgumentParser(description="ADB Control: airplane mode, reboot, status or network type.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--airplane", action="store_true", help="Enable/disable airplane mode")
    group.add_argument("-r", "--reboot", action="store_true", help="Reboot device")
    group.add_argument("-s", "--status", action="store_true", help="Check airplane mode status")
    group.add_argument("-c", "--connectivity_type", action="store_true", help="Check current network type")
    group.add_argument("-l", "--list", action="store_true", help="List all connected devices with brand info")
    parser.add_argument("--id", type=str, help="Device serial (optional)")

    args = parser.parse_args()
    manager = DeviceManager()

    # If no arguments are passed, list devices by default
    if not any(vars(args).values()):
        if not manager.devices:
            print("No devices connected.")
            parser.print_help()
            return
        manager.list_devices()
        return

    if args.list:
        manager.list_devices()
        return

    # For status: if multiple devices, show all statuses in table, else select device
    if args.status:
        if not manager.devices:
            print("No devices connected.")
            parser.print_help()
            return
        if len(manager.devices) == 1 or args.id:
            device_serial = manager.select_device(args.id)
            manager.check_device_status(device_serial)
        else:
            manager.check_device_status(device=None)
        return

    device_serial = manager.select_device(args.id)

    if args.airplane:
        manager.auto_toggle_airplane_mode(device_serial)
    elif args.reboot:
        manager.reboot_device(device_serial)
    elif args.connectivity_type:
        manager.monitor_connectivity_type(device_serial)

if __name__ == "__main__":
    main()