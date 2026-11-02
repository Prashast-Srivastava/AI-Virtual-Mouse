# 🖐️ AI Virtual Mouse

Control your computer's mouse cursor with nothing but your hand. This project uses your webcam, **MediaPipe** hand landmark detection, and **OpenCV** to track your fingers in real time and translate gestures into cursor movement and clicks via **PyAutoGUI**.

No special hardware needed, just a standard webcam.

---

## ✨ Features

- **Real-time hand tracking** using MediaPipe's Hand Landmarker (21 landmarks per hand)
- **Cursor control** by moving your index finger
- **Click gesture** by pinching your index and middle fingertips together
- **Smooth cursor motion** with a configurable smoothing factor to reduce jitter
- **Active-area box** drawn on screen so you know where your hand is tracked
- **Live FPS counter** and landmark overlay for easy debugging
- **Auto-download of the model**: `hand_landmarker.task` is fetched automatically if missing

---

## 🎮 How It Works

| Gesture | Fingers Up | Action |
|---|---|---|
| **Move** | Index finger only | Cursor follows your index fingertip |
| **Click** | Index + middle fingers, brought together (distance < 40 px) | Left click (0.5 s cooldown) |

**Pipeline overview:**

1. The webcam frame is captured and mirrored horizontally.
2. MediaPipe detects the hand and returns 21 landmarks.
3. `fingersUp()` determines which fingers are raised.
4. In **moving mode**, the index fingertip position inside the active rectangle is mapped to full-screen coordinates using `np.interp`, then smoothed before being passed to `pyautogui.moveTo`.
5. In **clicking mode**, the distance between the index and middle fingertips is measured; when it drops below the threshold, a click is fired.

---

## 📁 Project Structure

```
AI-Virtual-Mouse/
├── AiVirtualMouse.py        # Main application: webcam loop, gesture logic, mouse control
├── HandTrackingModule.py    # Reusable hand detection wrapper (MediaPipe Tasks API)
├── hand_landmarker.task     # MediaPipe hand landmark model
└── README.md
```

---

## 🛠️ Requirements

- Python 3.8+
- A working webcam
- Python packages:
  - `opencv-python`
  - `numpy`
  - `mediapipe`
  - `pyautogui`

---

## 🚀 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Prashast-Srivastava/AI-Virtual-Mouse.git
   cd AI-Virtual-Mouse
   ```

2. **(Optional) Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS / Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install opencv-python numpy mediapipe pyautogui
   ```

---

## ▶️ Usage

```bash
python AiVirtualMouse.py
```

- Raise your **index finger** and move it inside the purple rectangle to move the cursor.
- Raise your **index and middle fingers** and pinch them together to click.
- Press **`q`** in the camera window to quit.

> 💡 Sit in a well-lit area and keep your hand clearly visible to the camera for the best tracking.

---

## ⚙️ Configuration

Tweak these values at the top of `AiVirtualMouse.py`:

| Variable | Default | Description |
|---|---|---|
| `wCam`, `hCam` | `960`, `540` | Camera capture resolution |
| `frameR` | `100` | Margin (px) around the active tracking area |
| `smoothening` | `7` | Higher = smoother but slower cursor; lower = faster but jittery |

The click distance threshold (`length < 40`) and click cooldown (`0.5` seconds) can also be adjusted in the clicking-mode block.

---

## 🧩 Using the Hand Tracking Module

`HandTrackingModule.py` can be reused in your own projects:

```python
import cv2
import HandTrackingModule as htm

cap = cv2.VideoCapture(0)
detector = htm.handDetector(maxHands=1)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if lmList:
        print(detector.fingersUp())   # e.g. [0, 1, 0, 0, 0]

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
```

**Main methods**

- `findHands(img, draw=True)`: runs detection and draws the hand skeleton
- `findPosition(img, handNo=0, draw=True)`: returns landmark list `[id, x, y]` and bounding box
- `fingersUp()`: returns a 5-element list (thumb → pinky) of 1/0 flags
- `findDistance(p1, p2, img)`: returns the pixel distance between two landmarks

---

## 🔧 Troubleshooting

- **Camera not opening:** change `cv2.VideoCapture(0)` to `1` (or another index) if you have multiple cameras.
- **Cursor feels laggy:** lower the `smoothening` value.
- **Cursor is jittery:** increase `smoothening`.
- **Model download fails:** manually download `hand_landmarker.task` from the [MediaPipe models page](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker) and place it in the project root.
- **macOS permissions:** grant your terminal/IDE camera and accessibility permissions so PyAutoGUI can control the mouse.

---

## 🔮 Future Improvements

- Right-click and double-click gestures
- Scroll and drag-and-drop gestures
- Volume / brightness control
- Multi-monitor support

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

---

## 📜 License

No license has been specified yet. Consider adding one (e.g., [MIT](https://choosealicense.com/licenses/mit/)) to let others know how they can use this project.

---

## 🙌 Acknowledgements

- [MediaPipe](https://developers.google.com/mediapipe) for hand landmark detection
- [OpenCV](https://opencv.org/) for video capture and drawing
- [PyAutoGUI](https://pyautogui.readthedocs.io/) for mouse control

---

**Author:** [Prashast Srivastava](https://github.com/Prashast-Srivastava)
