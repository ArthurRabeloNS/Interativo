# GestureFlow 🖐️
### Gesture-Based Desktop Control Using Computer Vision

**GestureFlow** is a Python project that allows users to control their computer's mouse and interact with the keyboard using only a camera and hand gestures.

Using computer vision and hand tracking, the system interprets gestures performed in front of the camera and translates them into desktop actions, such as moving the cursor, clicking, dragging objects, scrolling through pages, and typing with a virtual keyboard.

This project was developed as a practical exploration of Python, desktop automation, and gesture recognition.

**Documentation:** English | [Versão em português](README_BR.md)

---

## ✨ Features

- 🖱️ **Mouse control:** move the cursor using your index finger.
- 👆 **Left click:** bring your thumb and index finger together to click.
- ✋ **Drag and drop:** hold the pinch gesture to drag objects.
- 👉 **Right click:** bring your thumb and middle finger together.
- 🤘 **Page scrolling:** use your index finger and little finger to control scrolling (up and down).
- ⌨️ **Virtual keyboard:** display an on-screen keyboard and type using gestures.
- 🔄 **Hand switching:** switch between the right and left hands.
- ⏸️ **Pause control:** temporarily suspend cursor control.
- 📷 **Live camera preview:** monitor hand tracking and system status in real time.

## 🛠️ Technologies

- **Python** — main programming language.
- **OpenCV** — camera capture and image processing.
- **MediaPipe** — hand detection and tracking.
- **NumPy** — numerical operations.
- **pynput** — mouse and keyboard control, including keyboard shortcuts.
- **Tkinter** — virtual keyboard interface.

## 📋 Requirements

Before running the project, make sure you have:

- Python installed.
- A working webcam.
- Windows recommended, since the project includes operating-system-specific behavior.
- An internet connection to install the dependencies.

## 📥 How to download

### 1. Clone the repository

Open a terminal and run:

```bash
git clone https://github.com/ArthurRabeloNS/GestureFlow.git
```

Navigate to the project directory:

```bash
cd GestureFlow
```

Alternatively, download the source code using **Code → Download ZIP** on the repository page.

### 2. Create a virtual environment (optional, recommended)

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install the dependencies

```bash
python -m pip install -r requirements.txt
```

```bash
python -m pip install opencv-python numpy mediapipe==0.10.14 pynput
```

The MediaPipe version is pinned to maintain compatibility with the `solutions` API used by the code.

### 4. Run the application

```bash
python controleDeDesktop.py
```

The camera window will open, and the application will begin tracking the selected hand.

## 🖐️ How to use

### Main gestures

| Gesture | Action |
|---|---|
| Index finger extended | Move the cursor |
| Thumb and index finger pinch | Left click when released |
| Hold the pinch for approximately 0.45 seconds | Drag objects |
| Thumb and middle finger pinch | Right click |
| Index and little fingers extended | Scroll by tilting the fingers up or down |
| Closed fist held for approximately 1.2 seconds | Show or hide the virtual keyboard |
| Open hand | Recognized by the system, but does not automatically pause the application |

### Keyboard shortcuts

| Key | Action |
|---|---|
| `F8` | Switch between the right and left hands |
| `F9` | Pause or resume control |
| `F10` | Show or hide the virtual keyboard |
| `F12` | Exit the application |
| `Q` or `ESC` | Exit through the camera window |
| `M` | Switch hands through the camera window |

**Tip:** keep your hand within the control area displayed in the camera preview and avoid sudden movements for smoother cursor control.

## ⚙️ Customization

The source code includes settings that can be adjusted to change how the system behaves, including:

- Camera index.
- Capture resolution.
- Initially selected hand.
- Image area used for cursor control.
- Pinch sensitivity.
- Drag activation delay.
- Scrolling speed.

These settings are defined near the beginning of `controleDeDesktop.py`.

## 🔒 Privacy and security

The application uses the camera to recognize gestures and perform actions locally on the computer. The current code does not implement image uploads to remote servers or video recording.

Because the application controls the real mouse and keyboard, test gestures in a safe environment and keep the application paused when it is not in use.

## 🎯 Project goals

GestureFlow explores alternative ways for people to interact with computers through computer vision, hand gesture recognition, and desktop automation.

It also provides an opportunity to learn about Python libraries, hand tracking, and alternative input interfaces.

---

Built as a learning project using Python and computer vision. 💻
