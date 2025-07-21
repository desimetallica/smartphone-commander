#!/usr/bin/env python3

import subprocess
import argparse
import sys
import re

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
    print("📱 Verifica dello stato del dispositivo...")
    status = get_airplane_mode_status(device_serial)
    if "enabled" in status:
        print("✈️ Stato: Modalità aereo ATTIVA")
    elif "disabled" in status:
        print("📶 Stato: Modalità aereo DISATTIVATA")
    else:
        print("❓ Stato: Modalità aereo SCONOSCIUTA")

def monitor_connectivity_type(device_serial):
    print("📡 Verifica dello stato della connessione dati...")

    # Mappa dei valori numerici
    network_type_map = {
        20: "5G (NR)",
        19: "4G+ (LTE_CA)",
        13: "4G (LTE)",
        10: "3G (HSPA)",
        3: "3G (UMTS)",
        1: "2G (GPRS)",
        0: "UNKNOWN"
    }

    # Mappa stringhe testuali
    string_type_map = {
        "NR": "5G (NR)",
        "LTE": "4G (LTE)",
        "LTE_CA": "4G+ (LTE CA)",
        "HSPA": "3G (HSPA)",
        "UMTS": "3G (UMTS)",
        "EDGE": "2G (EDGE)",
        "GPRS": "2G (GPRS)",
        "UNKNOWN": "Sconosciuto"
    }

    try:
        output = subprocess.check_output(
            ["adb", "-s", device_serial, "shell", "dumpsys", "telephony.registry"],
            encoding="utf-8",
            stderr=subprocess.DEVNULL
        )

        # Cerca valori numerici noti
        num_fields = [
            r"mDataNetworkType=(\d+)",
            r"getDataNetworkType=(\d+)",
            r"DataNetworkType=(\d+)",
        ]
        for pattern in num_fields:
            match = re.findall(pattern, output)
            if match:
                value = int(match[-1])
                print(f"🌐 Connettività attuale: {network_type_map.get(value, f'Altro ({value})')}")
                return

        # Cerca stringhe descrittive
        str_fields = [
            r"mNetworkType=([A-Z_]+)",
            r"accessNetworkTechnology=([A-Z_]+)",
            r"dataNetworkType=([A-Z_]+)",
            r"type=([A-Z_]+)",  # e.g., type=NR in mServiceState
        ]
        for pattern in str_fields:
            match = re.findall(pattern, output)
            if match:
                net_type = match[-1].strip().upper()
                print(f"🌐 Connettività attuale: {string_type_map.get(net_type, net_type)}")
                return

        print("❌ Impossibile determinare lo stato della connessione.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante l'esecuzione di adb: {e}")

def main():
    parser = argparse.ArgumentParser(description="Controllo ADB: modalità aereo, reboot, stato o tipo di rete.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--airplane", action="store_true", help="Abilita/disabilita la modalità aereo")
    group.add_argument("-r", "--reboot", action="store_true", help="Riavvia il dispositivo")
    group.add_argument("-s", "--status", action="store_true", help="Verifica lo stato della modalità aereo")
    group.add_argument("-c", "--connectivity_type", action="store_true", help="Verifica tipo di rete attuale")
    parser.add_argument("--id", type=str, help="Seriale del dispositivo (facoltativo)")

    args = parser.parse_args()
    device_serial = args.id if args.id else get_connected_device_serial()

    if args.airplane:
        auto_toggle_airplane_mode(device_serial)
    elif args.reboot:
        reboot_device(device_serial)
    elif args.status:
        check_device_status(device_serial)
    elif args.connectivity_type:
        monitor_connectivity_type(device_serial)

if __name__ == "__main__":
    main()
