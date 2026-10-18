# 📸 Magic Camera (projetoDeCamera)

🌐 **Idiomas / Languages:** [Português 🇧🇷](./README.md) | [English 🇺🇸](./README.en.md)

An interactive camera built in **Python**, controlled **only with your hands and face**. You paint in the air with your finger, switch colors by showing fingers, take a photo by closing your fist, open the menu by holding your finger over a button, and you can even play a bubble-popping game. Everything runs in real time through your webcam, using **OpenCV** and **MediaPipe**.

> ⚠️ **Note:** the program's on-screen interface (menu labels, messages, hints) is in **Portuguese**. This README keeps the exact on-screen labels in `code style` and explains what each one does in English.

---

## 📑 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [How to use](#-how-to-use)
- [Gestures](#-gestures)
- [On-screen interface](#-on-screen-interface)
- [Menu](#-menu)
- [Keyboard shortcuts](#-keyboard-shortcuts)
- [Bubble game](#-bubble-game)
- [Generated files](#-generated-files)
- [Settings in the code](#-settings-in-the-code)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

- 🎨 **Air painting** with your index finger, with 4 brush types, 5 sizes and symmetry (kaleidoscope).
- 🌈 **Color switching with your other hand**, by showing one finger (includes an animated rainbow color).
- 📏 **Brush size and eraser through gestures**.
- 📷 **Photo with a fist**, with an optional 3 or 5 second timer.
- 🎥 **Video recording** to MP4.
- 🖼️ **Backgrounds, filters and extra light** (including blurred background and "only you").
- 🧑 **Face mesh and hand skeleton** in 3 styles (mesh, neon, dots).
- 😮 **Mouth effect:** opening your mouth releases confetti.
- 😉 **Wink** to undo and redo (optional).
- 🫧 **30-second bubble game** with combos and a saved high score.
- 🖐️ **Gesture-controlled menu**: no mouse needed.

---

## 🧰 Requirements

- **Python 3.9 to 3.12** (recommended, for MediaPipe compatibility).
- A working **webcam**.
- Libraries:
  - `opencv-python`
  - `numpy`
  - `mediapipe==0.10.14` (very recent versions may not work with this code)
- Good lighting and keeping your hands visible to the camera helps a lot.
- **Sounds** work **on Windows only** (they use `winsound`). On other systems the program works normally, just without sound.

---

## 📥 Installation

1. **Download the project** (clone the repository or download the `projetoDeCamera.py` file).

   ```bash
   git clone https://github.com/ArthurRabeloNS/Jogos_Games.git
   ```

   > Adjust the link/folder to match the repository where the project lives.

2. **(Optional) Create a virtual environment:**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux / macOS
   source venv/bin/activate
   ```

3. **Install the dependencies:**

   ```bash
   python -m pip install opencv-python numpy mediapipe==0.10.14
   ```

4. **Run it:**

   ```bash
   python projetoDeCamera.py
   ```

A window named **"Camera"** will open showing your camera feed. To quit, press **Q** or **Esc** (or close the window).

---

## ▶️ How to use

1. Open the program and face the camera with both hands visible.
2. Make the **peace sign (V)** with your brush hand to turn painting on, then raise **only your index finger** to draw.
3. With your other hand, show **one finger** to pick a color.
4. To change settings, **hold your index finger for 2 seconds** over the **MENU** button (top-right corner), or press **M**.
5. To see the quick guide inside the program, press **H**.

> 💡 **Brush hand:** by default it's the **right hand** (right-handed mode). If you're left-handed, switch it in the menu (**Voce e**) or press **T**. The other hand becomes the **color hand**.

---

## 🖐️ Gestures

### Brush hand (the dominant one)

| Gesture | What it does |
|---|---|
| ✌️ **Peace sign (V)** | Turns painting on ("arms" the brush). |
| ☝️ **Only the index finger raised** | Paints while you move your finger. |
| 🖐️ **Lowering the finger** (open hand or finger down) | Ends the current stroke. There's a 0.3 s tolerance so strokes aren't cut by accident. |
| ✊ **Fist** (coming from an open hand) | Takes a **photo**. |

If you turn painting on and don't draw for **8 seconds**, it turns itself off (just make the V again).

### Color hand (the other one)

| Gesture | What it does |
|---|---|
| ☝️ **1 finger raised** | Picks the color: **thumb** = yellow, **index** = red, **middle** = green, **ring** = blue, **pinky** = rainbow. |
| 🤏 **"L"** (thumb + index) | Adjusts the brush **size**. The wider the L, the bigger the brush. |
| ✊ **Fist** (no fingers raised) | Becomes the **eraser**. It erases with a circle larger than the brush. |

### Face

| Gesture | What it does |
|---|---|
| 😮 **Open your mouth** | Releases confetti and shows the mouth meter (and the text "AAAAAH!"). |
| 😉 **Wink the left eye** | Undoes the last stroke. |
| 😉 **Wink the right eye** | Redoes the undone stroke. |

> Winking must be held for about half a second and is **off** by default (turn it on in **EXTRAS > Piscadinha**).

---

## 🖥️ On-screen interface

| Element | Where | What it's for |
|---|---|---|
| **MENU button** | Top-right corner | Hold your index finger on it for 2 s to open. When the menu is open it becomes **FECHAR** (close). A bar fills up to show progress. |
| **Color palette** | Bottom-left | 5 dots (`pol`, `ind`, `med`, `ane`, `min`) showing the colors. The active color has a white ring. |
| **Cyan cursor** | Index fingertip | Shows up when you point with your index finger (to use the menu). |
| **White circle** | Index fingertip | Shows the brush size while painting is on. Turns **red** when it's the eraser. |
| **Colored dots on fingers** | Color hand | Show which finger is which color. The chosen finger has a white ring. |
| **Mouth meter** | Right side | A bar that rises as you open your mouth wider. |
| **REC 00:00** | Top, center | Appears while a video is being recorded. |
| **Countdown** | Center of the screen | Big number for the photo timer. |
| **Notices** | Bottom | Quick messages ("Foto salva", "DESFEITO", etc.). |
| **Texts and FPS** | Top-left | Style, brush and size (and symmetry, if on), the gesture detected on the brush hand, the **FPS** and the current color name. Can be hidden with **Textos na tela**. |
| **PINCEL / COR labels** | Near each hand's wrist | Show which hand is the brush hand and which is the color hand. |
| **Painting status** | Top-left (green) | `PINTURA LIGADA: levante so o indicador` (painting on: raise only your index finger), `PINTANDO...` (painting) or `BORRACHA...` (erasing). |
| **Item hint** | Inside the menu | A short explanation of the button you're pointing at. |
| **X button** | Menu panel corner | Closes the menu (hold for 0.8 s). |
| **White flash** | Whole screen | Quick effect when a photo is taken. |

---

## 📋 Menu

**How to open it:** hold your index finger on the **MENU** button for **2 s** (or press **M**).

**How to use it:**
- Point with **only one finger** of your brush hand and **hold over the button you want**. A bar fills up and, when full, the action happens.
- **Tabs** and **FECHAR/X** take about **0.8 s**. **Items** take about **1.1 s**.
- On items that **cycle through options** (marked with 🔁 below), if you keep holding, it moves to the next option over and over.

The menu has 3 tabs:

### 🎨 DESENHO tab (Drawing)

| On-screen item | What it does |
|---|---|
| **Voce e** | Switches between `DESTRO` (right-handed: brush on the right hand) and `CANHOTO` (left-handed: brush on the left hand). |
| **Pincel** 🔁 | Changes the brush type: `LISO` (smooth), `NEON` (glows), `SPRAY` (airbrush) or `FAISCAS` (sparks while drawing). |
| **Tamanho** 🔁 | Steps through sizes `4`, `8`, `14`, `24` and `36 px`. You can also adjust it with the "L" gesture. |
| **Simetria** 🔁 | `OFF`, `ESPELHO` (mirror), `4x`, `6x`, `8x` and `8x ESPELHO`. Repeats your stroke around the center, like a kaleidoscope. |
| **Desfazer** | Undoes the last stroke (key **Z**). |
| **Refazer** | Redoes the undone stroke (key **Y**). |
| **Limpar tudo** | Erases the whole drawing (can be undone with **Z**). |
| **Salvar desenho** | Saves only the drawing as a **transparent PNG** (key **S**). |

### 🖼️ VISUAL tab

| On-screen item | What it does |
|---|---|
| **Estilo** 🔁 | How face and hands appear: `MALHA` (mesh), `NEON` or `PONTOS` (dots) (keys **1**, **2**, **3**). |
| **Fundo** 🔁 | Background: `AUTO`, `CAMERA`, `ESCURO`, `PRETO`, `BRANCO`, `DESFOCADO` or `SO VOCE`. |
| **Filtro** 🔁 | `NORMAL`, `P&B` (black & white), `SEPIA`, `NEGATIVO`, `TERMICO` (thermal), `PIXEL`, `ESBOCO` (sketch) or `CARTUM` (cartoon). |
| **Luz extra** 🔁 | Extra light: `OFF`, `AUTO` or `FORTE` (strong). Brightens the video in dark rooms and helps the camera find your hands. |
| **Mostrar rosto** | Turns the face mesh on or off. |
| **Mostrar maos** | Turns the hand skeleton on or off. |
| **Textos na tela** | Turns the on-screen texts and FPS on or off. |
| **Efeito da boca** | Turns the mouth confetti and meter on or off. |

**About the backgrounds:**

| Option | Result |
|---|---|
| `AUTO` | Uses a **black** background in NEON style and the **camera** in other styles. |
| `CAMERA` | Shows the normal camera image. |
| `ESCURO` | Darkens the camera image. |
| `PRETO` / `BRANCO` | Solid black / white background. |
| `DESFOCADO` | Keeps you sharp and blurs the rest of the scene. |
| `SO VOCE` | Keeps only you and turns the rest black. |

### ⭐ EXTRAS tab

| On-screen item | What it does |
|---|---|
| **Jogo de bolhas** | Starts (`JOGAR`) or stops (`PARAR`) the bubble game. The menu closes when it starts. |
| **Gravar video** | Starts or stops MP4 recording (key **R**). |
| **Timer da foto** 🔁 | `OFF`, `3 s` or `5 s` countdown before the fist photo. |
| **Foto (punho)** | Turns the photo-by-fist on or off. |
| **Pintura (V)** | Turns painting by V gesture on or off. |
| **Piscadinha** | Turns undo/redo by winking on or off (off by default). |
| **Sons** | Turns sound effects on or off (Windows only). |
| **Ajuda** | Opens the quick guide for gestures and keys (key **H**). |

> The items **Foto (punho)**, **Pintura (V)**, **Piscadinha**, **Sons**, **Mostrar rosto**, **Mostrar maos**, **Textos na tela** and **Efeito da boca** show `LIGADO` (on, green) or `DESLIGADO` (off, red).

---

## ⌨️ Keyboard shortcuts

| Key | Action |
|---|---|
| **1 / 2 / 3** | Style: mesh, neon, dots |
| **P** | Turns painting on (no need to make the V) |
| **Z** | Undo |
| **Y** | Redo |
| **C** | Clear the drawing |
| **S** | Save the drawing as a transparent PNG |
| **R** | Start/stop video recording |
| **Space** | Take a photo right now |
| **T** | Switch the brush hand (right/left-handed) |
| **M** | Open/close the menu |
| **H** | Show/hide help |
| **F** | Fullscreen |
| **Q** or **Esc** | Quit |

---

## 🫧 Bubble game

Open it from the menu at **EXTRAS > Jogo de bolhas**.

- ⏱️ Duration: **30 seconds**.
- 👆 Pop bubbles by touching them with your **fingertips** (either hand). You can also pop them with an **open mouth**.
- 🫧 **Regular bubbles:** +1 point.
- 🟡 **Golden bubbles:** +5 points.
- 🔴 **Red bubbles (bombs):** −3 points and reset your combo. **Avoid them!**
- 🔥 **Combo:** popping several in a row (less than 1.2 s apart) gives bonus points. From combo 3 on, the game shows `COMBO xN`.
- 🚀 Bubbles get **faster and more frequent** as time goes by.
- 🏆 The **high score** is saved in the `recorde.txt` file, in the program folder.

While the game is running, painting and the fist photo are disabled.

---

## 📂 Generated files

Everything is saved automatically in the **`fotos/`** folder, created next to the program:

| File | Source |
|---|---|
| `foto_YYYYMMDD_HHMMSS.png` | Photo (fist or **Space** key), including drawing and effects, without the menu buttons. |
| `desenho_YYYYMMDD_HHMMSS.png` | Only the drawing, with a transparent background. |
| `video_YYYYMMDD_HHMMSS.mp4` | Video recording. |

In addition, the **`recorde.txt`** file (in the program folder) stores the bubble game's high score.

---

## ⚙️ Settings in the code

At the top of the `projetoDeCamera.py` file you can adjust:

| Variable | What it does |
|---|---|
| `CAMERA_INDEX` | Which camera to use (`0` is the default). Change it if you have more than one. |
| `RESOLUCAO` | Camera resolution, e.g. `(1280, 720)`. `None` uses the default. |
| `DWELL_MENU` | Time to open the menu (default `2.0` s). |
| `DWELL_ITEM` | Time to activate a menu item (default `1.1` s). |
| `DWELL_ABA` | Time to switch tabs or close (default `0.8` s). |
| `GRACA_TRACO` | Tolerance before a stroke is cut (default `0.30` s). |
| `TEMPO_ARMADA` | Time until painting turns itself off (default `8.0` s). |
| `DURACAO_JOGO` | Bubble game duration (default `30` s). |

---

## 🛠️ Troubleshooting

| Problem | What to do |
|---|---|
| **"Nao consegui abrir a camera"** (couldn't open the camera) | Close other programs that use the camera (Zoom, Teams, browser...) or change `CAMERA_INDEX`. |
| **"Seu mediapipe e novo demais"** (your mediapipe is too new) | Run `python -m pip install mediapipe==0.10.14`. |
| **Gestures aren't recognized** | Improve the lighting, keep your whole hand visible and turn on **Luz extra** in the menu. |
| **Painting won't turn on** | Check that **Pintura (V)** is `LIGADO`, that the menu is closed and that the game isn't running. |
| **I'm painting with the wrong hand** | Switch it in **Voce e** or press **T**. |
| **"Fundo indisponivel neste mediapipe"** notice | `DESFOCADO` and `SO VOCE` depend on MediaPipe's segmentation. The program falls back to the `AUTO` background. |
| **No sound** | Sounds only work on Windows and must be `LIGADO` in **Sons**. |
| **It's slow** | Close other programs, use a smaller `RESOLUCAO` and leave **Filtro** on `NORMAL`. |

---

## 🧱 Technologies

- [Python](https://www.python.org/)
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe) (face, hands and segmentation)
- [NumPy](https://numpy.org/)

---

Made by **Arthur Rabelo** 💻 · [GitHub](https://github.com/ArthurRabeloNS)