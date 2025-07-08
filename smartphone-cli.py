import subprocess
import argparse
import sys

def get_connected_device_serial():
    try:
        output = subprocess.check_output(["adb", "devices"], encoding="utf-8")
        lines = output.strip().splitlines()[1:]
        devices = [line.split()[0] for line in lines if "\tdevice" in line]

        if not devices:
            print("❌ Nessun dispositivo connesso via ADB.")
            sys.exit(1)

        print(f"✅ Dispositivo trovato: {devices[0]}")
        return devices[0]
    except subprocess.CalledProcessError:
        print("❌ Errore eseguendo 'adb devices'")
        sys.exit(1)

def get_airplane_mode_status(device):
    try:
        output = subprocess.check_output(
            ["adb", "-s", device, "shell", "cmd", "connectivity", "airplane-mode"],
            encoding="utf-8"
        ).strip()
        print(f"📡 Modalità aereo attuale: {output}")
        return output
    except subprocess.CalledProcessError as e:
        print("❌ Errore ottenendo lo stato della modalità aereo.")
        print(f"⚠️  Messaggio: {e}")
        sys.exit(1)

def set_airplane_mode(device, enable: bool):
    state = "enable" if enable else "disable"
    try:
        subprocess.run(
            ["adb", "-s", device, "shell", "cmd", "connectivity", "airplane-mode", state],
            check=True
        )
        print(f"✅ Modalità aereo {'abilitata' if enable else 'disabilitata'}.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore nell'impostare la modalità aereo a '{state}'")
        print(f"⚠️  Messaggio: {e}")

def auto_toggle_airplane_mode(device):
    status = get_airplane_mode_status(device)
    if "enabled" in status:
        print("📴 Modalità aereo già abilitata ➡ disabilitazione...")
        set_airplane_mode(device, False)
    elif "disabled" in status:
        print("📶 Modalità aereo disattivata ➡ abilitazione...")
        set_airplane_mode(device, True)
    else:
        print("⚠️ Stato modalità aereo non riconosciuto.")

def reboot_device(device_serial):
    print("🔄 Avvio del riavvio del dispositivo...")
    try:
        subprocess.run(["adb", "-s", device_serial, "reboot"], check=True)
        print("✅ Riavvio eseguito correttamente.")
    except subprocess.CalledProcessError as e:
        print("❌ Errore durante il riavvio del dispositivo.")
        print(f"⚠️  Messaggio: {e}")

def check_device_status(device_serial):
    """Check and print the current airplane mode status without changing it."""
    print("📱 Verifica dello stato del dispositivo...")
    status = get_airplane_mode_status(device_serial)
    if "enabled" in status:
        print("✈️ Stato: Modalità aereo ATTIVA")
    elif "disabled" in status:
        print("📶 Stato: Modalità aereo DISATTIVATA")
    else:
        print("❓ Stato: Modalità aereo SCONOSCIUTA")

def main():
    parser = argparse.ArgumentParser(description="Controllo ADB: modalità aereo o reboot del telefono.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--airplane", action="store_true", help="Abilita/disabilita la modalità aereo")
    group.add_argument("-r", "--reboot", action="store_true", help="Riavvia il dispositivo")
    group.add_argument("-s", "--status", action="store_true", help="Verifica lo stato della modalità aereo")
    parser.add_argument("--id", type=str, help="Seriale del dispositivo (facoltativo)")

    args = parser.parse_args()

    device_serial = args.id if args.id else get_connected_device_serial()

    if args.airplane:
        auto_toggle_airplane_mode(device_serial)
    elif args.reboot:
        reboot_device(device_serial)
    elif args.status:
        check_device_status(device_serial)

if __name__ == "__main__":
    main()
