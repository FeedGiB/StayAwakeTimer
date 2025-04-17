# Stay Awake App - Mouse Mover to Prevent Sleep
# Author: Alex Sharek
# Description: Smart utility that moves your mouse to keep your system awake. Now moves from and returns to your current cursor position, and runs shapes over 5 seconds for visibility.

import pyautogui
import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import json
import os
import sys
import platform
from math import cos, sin, pi

# ========== CONFIG + STATE ==========
CONFIG_PATH = "settings.json"
DEFAULT_CONFIG = {
    "interval_seconds": 300,
    "movement_mode": "circle",
    "dark_mode": "auto",
    "last_position": [100, 100]
}

# Try to detect system dark mode on Windows
try:
    import ctypes
    def is_dark_mode():
        try:
            if platform.system() == "Windows":
                registry = ctypes.windll.advapi32
                hKey = ctypes.c_void_p()
                result = registry.RegOpenKeyExW(
                    0x80000001,
                    "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                    0,
                    0x20019,
                    ctypes.byref(hKey)
                )
                if result == 0:
                    value = ctypes.c_int()
                    size = ctypes.c_uint(4)
                    registry.RegQueryValueExW(hKey, "AppsUseLightTheme", 0, None, ctypes.byref(value), ctypes.byref(size))
                    registry.RegCloseKey(hKey)
                    return value.value == 0
        except:
            pass
        return False
except ImportError:
    def is_dark_mode():
        return False

# Load config
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

INTERVAL_SECONDS = config.get("interval_seconds", 300)
MODE = config.get("movement_mode", "circle")
DARK_MODE_SETTING = config.get("dark_mode", "auto")
LAST_X, LAST_Y = config.get("last_position", [100, 100])
DARK_MODE = is_dark_mode() if DARK_MODE_SETTING == "auto" else DARK_MODE_SETTING == "true"

# App state
start_time = time.time()
move_count = 0
remaining_time = INTERVAL_SECONDS
paused = False
last_move_timestamp = "N/A"

# ========== INTERVAL OPTIONS ==========
INTERVAL_OPTIONS = {
    "15 seconds": 15,
    "30 seconds": 30,
    "1 minute": 60,
    "2 minutes": 120,
    "3 minutes": 180,
    "4 minutes": 240,
    "5 minutes": 300,
    "10 minutes": 600,
    "15 minutes": 900
}
REVERSE_INTERVAL_OPTIONS = {v: k for k, v in INTERVAL_OPTIONS.items()}

# ========== MOVEMENT LOGIC ==========
def move_shape(sides, star=False):
    # Get current mouse position to use as center
    start_x, start_y = pyautogui.position()
    points = []

    # Build shape points around current position
    for i in range(sides):
        angle = (4 if star else 2) * pi * i / sides
        x = start_x + 50 * cos(angle)
        y = start_y + 50 * sin(angle)
        points.append((x, y))

    # Total duration for shape: 5 seconds
    step_duration = 5.0 / len(points)

    for x, y in points:
        pyautogui.moveTo(x, y, duration=step_duration)

    pyautogui.moveTo(start_x, start_y, duration=step_duration)  # return to start

def move_mouse():
    global move_count, last_move_timestamp
    try:
        if MODE == "circle": move_shape(36)
        elif MODE == "square": move_shape(4)
        elif MODE == "triangle": move_shape(3)
        elif MODE == "pentagon": move_shape(5)
        elif MODE == "star": move_shape(5, star=True)
        elif MODE == "wiggle":
            center_x, center_y = pyautogui.position()
            step_duration = 5.0 / 12  # Approx 12 wiggle points
            for offset in range(-25, 25, 5):
                pyautogui.moveTo(center_x + offset, center_y, duration=step_duration)
            pyautogui.moveTo(center_x, center_y, duration=step_duration)
        else:
            move_shape(36)

        move_count += 1
        last_move_timestamp = time.strftime("%H:%M:%S", time.localtime())
        print(f"Moved at {last_move_timestamp}")
    except Exception as e:
        print("Error in movement:", e)
        time.sleep(2)
        move_mouse()

# ========== TIMER AND UI UPDATE ==========
def countdown_and_move():
    global remaining_time
    if not paused:
        if remaining_time > 0:
            remaining_time -= 1
        else:
            move_mouse()
            remaining_time = INTERVAL_SECONDS
    update_gui()
    root.after(1000, countdown_and_move)

def update_gui():
    mins, secs = divmod(remaining_time, 60)
    countdown_label.config(text=f"Next move in: {mins:02}:{secs:02}")
    move_label.config(text=f"Moves made: {move_count}")

    elapsed = int(time.time() - start_time)
    d, rem = divmod(elapsed, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    runtime_label.config(text=f"Running time: {d}d {h:02}h {m:02}m {s:02}s")

    last_move_label.config(text=f"Last move at: {last_move_timestamp}")
    progress_var.set(INTERVAL_SECONDS - remaining_time)
    pause_button.config(text="Resume" if paused else "Pause")

def toggle_pause():
    global paused
    paused = not paused
    update_gui()

# ========== SETTINGS WINDOW ==========
def open_settings():
    win = tk.Toplevel(root)
    win.title("Settings")
    win.configure(bg=bg_color)

    geo = root.geometry()
    cur_x = root.winfo_x()
    cur_y = root.winfo_y()
    win.geometry(f"+{cur_x + 400}+{cur_y}")

    tk.Label(win, text="Interval:", bg=bg_color, fg=fg_color, font=font_main).grid(row=0, column=0, sticky='e', padx=10, pady=5)
    interval_var = tk.StringVar(value=REVERSE_INTERVAL_OPTIONS.get(INTERVAL_SECONDS, "5 minutes"))
    ttk.Combobox(win, textvariable=interval_var, font=font_main, values=list(INTERVAL_OPTIONS.keys())).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(win, text="Mode:", bg=bg_color, fg=fg_color, font=font_main).grid(row=1, column=0, sticky='e', padx=10, pady=5)
    mode_var = tk.StringVar(value=MODE)
    ttk.Combobox(win, textvariable=mode_var, values=["circle", "square", "triangle", "pentagon", "star", "wiggle"], font=font_main).grid(row=1, column=1, padx=10, pady=5)

    tk.Label(win, text="Dark Mode:", bg=bg_color, fg=fg_color, font=font_main).grid(row=2, column=0, sticky='e', padx=10, pady=5)
    dark_mode_var = tk.StringVar(value=DARK_MODE_SETTING)
    ttk.Combobox(win, textvariable=dark_mode_var, values=["true", "false", "auto"], font=font_main).grid(row=2, column=1, padx=10, pady=5)

    def save_settings():
        x, y = root.winfo_x(), root.winfo_y()
        new_config = {
            "interval_seconds": INTERVAL_OPTIONS.get(interval_var.get(), 300),
            "movement_mode": mode_var.get(),
            "dark_mode": dark_mode_var.get(),
            "last_position": [x, y]
        }
        with open(CONFIG_PATH, 'w') as f:
            json.dump(new_config, f, indent=4)
        tk.Label(win, text="Settings saved. Restarting...", bg=bg_color, fg=fg_color, font=("Segoe UI", 10)).grid(row=4, columnspan=2, pady=5)
        root.after(1200, lambda: os.execl(sys.executable, sys.executable, *sys.argv))

    tk.Button(win, text="Save", command=save_settings, font=font_main).grid(row=3, columnspan=2, pady=10)

# ========== MAIN UI ==========
root = tk.Tk()
root.title("Stay Awake")
root.attributes("-topmost", True)
root.resizable(True, True)
root.geometry(f"+{LAST_X}+{LAST_Y}")

font_main = ("Segoe UI", 12)
font_title = ("Segoe UI", 16)

bg_color = "#1e1e1e" if DARK_MODE else "#f0f0f0"
fg_color = "#ffffff" if DARK_MODE else "#000000"
root.configure(bg=bg_color)

countdown_label = tk.Label(root, text="", font=font_title, bg=bg_color, fg=fg_color)
countdown_label.pack(padx=20, pady=10)

move_label = tk.Label(root, text="", font=font_title, bg=bg_color, fg=fg_color)
move_label.pack(padx=20, pady=10)

runtime_label = tk.Label(root, text="", font=font_main, bg=bg_color, fg=fg_color)
runtime_label.pack(padx=20, pady=(0, 10))

last_move_label = tk.Label(root, text="Last move at: N/A", font=font_main, bg=bg_color, fg=fg_color)
last_move_label.pack(padx=20, pady=(0, 10))

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=INTERVAL_SECONDS, length=300)
progress_bar.pack(padx=20, pady=(0, 10))

pause_button = tk.Button(root, text="Pause", font=font_main, command=toggle_pause)
pause_button.pack(padx=20, pady=(0, 5))

settings_button = tk.Button(root, text="Settings", font=font_main, command=open_settings)
settings_button.pack(padx=20, pady=(0, 10))

root.after(1000, countdown_and_move)
root.mainloop()