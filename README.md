# Stay Awake Timer – Mouse Mover Utility

Smart utility that keeps your system awake by moving the mouse in shapes at set intervals.

**Author:** Alex Sharek  
**Status:** Actively used | GUI-based | Configurable | macOS/Windows compatible

---

## Features

- Keeps your computer awake using gentle cursor motion
- Supports **circle, triangle, square, pentagon, star, and wiggle** patterns
- Built-in **dark mode** detection (Windows only) + cross-platform safe fallback
- Fully customizable via `settings.json`:
  - Time intervals (15s to 15m)
  - Movement mode
  - Dark mode toggle
- Modern GUI with:
  - Countdown timer
  - Move tracker
  - Live runtime
  - Settings panel
  - Restart on config change

---

## 🖥Tech Stack

- Python 3
- `tkinter` (GUI)
- `pyautogui` (mouse control)
- JSON (persistent config)
- `ctypes` (Windows registry query)

---

## How to Run

1. Install dependencies:
   ```bash
   pip install pyautogui
