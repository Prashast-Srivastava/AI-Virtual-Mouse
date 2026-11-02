import cv2
import os
import math
import time
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/"
             "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "hand_landmarker.task")

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, minTrackCon=0.5):
        self.maxHands = maxHands
        self.tipIds = [4, 8, 12, 16, 20]

        if not os.path.exists(MODEL_PATH):
            print("Downloading hand_landmarker.task ...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=maxHands,
            min_hand_detection_confidence=detectionCon,
            min_hand_presence_confidence=detectionCon,
            min_tracking_confidence=minTrackCon,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.results = None
        self.lmList = []
        self.handLabel = "Right"
        self.startTime = time.time()
        self.lastTs = -1

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mpImage = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)

        ts = int((time.time() - self.startTime) * 1000)
        if ts <= self.lastTs:
            ts = self.lastTs + 1
        self.lastTs = ts

        self.results = self.landmarker.detect_for_video(mpImage, ts)

        if draw and self.results.hand_landmarks:
            h, w, _ = img.shape
            for hand in self.results.hand_landmarks:
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand]
                for a, b in HAND_CONNECTIONS:
                    cv2.line(img, pts[a], pts[b], (0, 255, 0), 2)
                for p in pts:
                    cv2.circle(img, p, 4, (0, 0, 255), cv2.FILLED)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList, yList = [], []
        bbox = ()
        self.lmList = []
        if self.results and self.results.hand_landmarks:
            if handNo >= len(self.results.hand_landmarks):
                return self.lmList, bbox
            hand = self.results.hand_landmarks[handNo]
            if self.results.handedness:
                self.handLabel = self.results.handedness[handNo][0].category_name
            h, w, _ = img.shape
            for id, lm in enumerate(hand):
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            bbox = (min(xList), min(yList), max(xList), max(yList))
            if draw:
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                              (bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)
        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        if len(self.lmList) < 21:
            return [0, 0, 0, 0, 0]
        # Thumb (compare x; direction depends on which hand, image is mirrored)
        if self.handLabel == "Right":
            fingers.append(1 if self.lmList[4][1] < self.lmList[3][1] else 0)
        else:
            fingers.append(1 if self.lmList[4][1] > self.lmList[3][1] else 0)
        # Other 4 fingers (tip above PIP joint)
        for id in range(1, 5):
            tip = self.tipIds[id]
            fingers.append(1 if self.lmList[tip][2] < self.lmList[tip - 2][2] else 0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True, r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]