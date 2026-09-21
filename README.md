# JARVIS Desktop Controller

A gesture-driven desktop control system powered by MediaPipe hand tracking and PyAutoGUI.

## What it does

This project turns hand movements into mouse and system actions in real time. Use one hand to move the cursor, pinch to click, scroll with two fingers, and trigger desktop navigation gestures with natural hand poses.

## Gestures

- **1 finger** — move cursor with smoothing
- **Pinch** — left click
- **2 fingers** — scroll
- **Palm (5 fingers)** — show desktop
- **Fist** — return to last app
- **3 fingers** — open Windows Task View and navigate apps

## How to run

```bash
cd jarvis-desktop-controller
python jarvis.py
```

Press `q` to quit.

## Notes

- Best used with a stable camera feed and good lighting.
- `pyautogui` handles cursor and click automation.
