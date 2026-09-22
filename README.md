# AirControl AI 🖐️

An AI-powered, hands-free desktop controller that uses **computer vision and hand gestures** to control the Windows desktop in real time.

AirControl AI uses **MediaPipe Hand Landmarker** for hand tracking and **PyAutoGUI** for desktop automation, allowing users to interact with their computer without physically touching the mouse.

## ✨ Features

* 🖱️ Real-time cursor movement using hand tracking
* 👌 Pinch gesture for left click
* ✌️ Two-finger scrolling
* ✋ Palm gesture to show the desktop
* ✊ Fist gesture for switching back to the previous application
* 🤟 Three-finger gesture for Windows Task View
* 🔄 Gesture stabilization to reduce accidental actions
* 🎯 Cursor smoothing for more natural movement
* 📷 Automatic camera fallback
* 🖥️ Full-screen visual interface
* ⚡ Real-time computer vision processing

## 🖐️ Gesture Controls

| Gesture           | Action                         |
| ----------------- | ------------------------------ |
| ☝️ One finger     | Move cursor                    |
| 👌 Pinch          | Left click                     |
| ✌️ Two fingers    | Scroll                         |
| ✋ Open palm       | Show desktop                   |
| ✊ Fist            | Switch to previous app         |
| 🤟 Three fingers  | Open Windows Task View         |
| 🔄 Toggle gesture | Enable / pause desktop control |


## 📸 Gesture Guide

![AirControl AI Hand Gestures Guide](Gesture-guide.jpeg)

## 🧠 How It Works

AirControl AI processes the camera feed through a real-time computer vision pipeline:

```text
Webcam
   ↓
MediaPipe Hand Landmarker
   ↓
Hand Landmark Detection
   ↓
Gesture Classification
   ↓
Gesture Stabilization
   ↓
PyAutoGUI
   ↓
Windows Desktop Action
```

The system detects hand landmarks, analyzes finger positions and hand geometry, classifies the gesture, stabilizes the detected gesture across multiple frames, and then translates the gesture into a desktop action.

## 🛠️ Tech Stack

* **Python 3.13**
* **MediaPipe**
* **OpenCV**
* **NumPy**
* **PyAutoGUI**

## 📁 Project Structure

```text
aircontrol-ai/
│
├── models/
│   └── hand_landmarker.task
│
├── .gitignore
├── jarvis.py
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/mhumyyunbaber-dot/aircontrol-ai.git
cd aircontrol-ai
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

Install the required packages:

```bash
pip install mediapipe opencv-python numpy pyautogui
```

## ▶️ Run the Project

Make sure your webcam is connected, then run:

```bash
python jarvis.py
```

AirControl AI will open its camera interface and begin detecting hand gestures.

Press:

```text
Q
```

to exit the application.

## 📷 Camera & Environment

For better tracking performance:

* Use a stable webcam.
* Keep your hand clearly visible.
* Use reasonable lighting.
* Avoid excessive background clutter.
* Keep your hand within the camera frame.

## 🔒 Safety & Control

Desktop control can be paused using the project's toggle gesture.

When control is paused, detected hand movements do not control the mouse or trigger desktop actions.

## 🚀 Future Improvements

Possible future development includes:

* Multi-hand interaction
* Custom user-defined gestures
* Voice + gesture hybrid control
* Gesture-controlled media playback
* Application-specific controls
* Improved gesture calibration
* Cross-platform desktop support
* More advanced gesture recognition

## 📌 Project Purpose

AirControl AI was built as a practical computer-vision project to explore how **hand landmark detection, gesture recognition, real-time processing, and desktop automation** can be combined into a usable human-computer interaction system.

## 👨‍💻 Author

**Humayun**

GitHub:
https://github.com/mhumyyunbaber-dot

---

⭐ If you find this project interesting, consider giving the repository a star.
